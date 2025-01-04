# REFERENCE - https://docs.python.org/3/howto/logging.html
# REFERENCE - https://stackoverflow.com/questions/8898997/python-clear-a-log-file

# External Imports
from copy import deepcopy
import logging
import datetime
from math import inf

# Internal Imports
from Game.Regicide.regicide_board import Result
from Game.Regicide.regicide_action import RegicideAction
from Game.Regicide.regicide_board import RegicideBoard
from ISMCTS.Game.regicide_node import RegicideNode
from ISMCTS.Base.timer import Timer

# PyInstaller Prompt
## Windows
### pyinstaller --onefile --add-data "Cards;Cards" --add-data "Game;Game" --add-data "ISMCTS;ISMCTS" ISMCTS/main.py
## macOS
###  pyinstaller --onefile \ --add-data "Cards:Cards" \ --add-data "Game:Game" \ --add-data "ISMCTS:ISMCTS" \ ISMCTS/main.py


def main():
    # CONFIG - Allow the ability to configure maximum runs and maximum time
    max_runs = validMaxRuns()
    max_time = validMaxTime() # in (s)
    action_state_logging = True
    time_logging = False
    result_logging = False
    main_game_state = RegicideBoard()
    main_game_state.start()

    # NOTE - turning off state and action log whilst taking timing results
    if action_state_logging:
        action_logger = initialiseActionLogger()
        state_logger = initialiseStateLogger()
        logState(state_logger, main_game_state)

    if time_logging:
        time_logger = initialiseTimeLogger()

    if result_logging:
        result_logger = initialiseResultLogger("Heavy")

    # Keep track of how many bosses were defeated
    boss_defeated = 0

    # Keep track of how many turns the players survive
    turns_survived = 0

    root_node = RegicideNode()

    game_over = False

    while not game_over:

        next_turn = main_game_state.currentPlayer()


        # NOTE - Player is currently set to player 1 - all other players are set to an AI
        if next_turn < 0: # Player's Turn
            current_player = main_game_state.players[next_turn]
            print("")
            print(current_player.name + "'s Turn:")

            main_game_state.displayHandLengths()

            current_boss = main_game_state.castle.boss
            legal_plays = main_game_state.legalPlays(current_player.hand)

            if len(legal_plays) == 0:
                game_over = True

            print("Boss:", current_boss,
                  "| Health:", current_boss.health,
                  "| Attack:", current_boss.attack)


            print(legal_plays)
            play_index = validPlay(legal_plays)
            print("")

            main_game_state = main_game_state.nextState(legal_plays[play_index])

            # NOTE - turning off state and action log whilst taking timing results
            if action_state_logging:
                logState(state_logger, main_game_state)

            # NOTE - duplicate code fragment - could make state check into it's own function
            state = main_game_state.winner()

            if state == Result.BOSS_DEFEATED:
                boss_defeated += 1
                turns_survived += 1

            elif state == Result.ALIVE:
                turns_survived += 1

            elif state != Result.ALIVE and state != Result.BOSS_DEFEATED:
                game_over = True

        else: # AI's Turn

            print("")
            print(main_game_state.players[main_game_state.currentPlayer()].name + "'s Turn:")

            main_game_state.displayHandLengths()

            print("Boss:", main_game_state.castle.boss,
                  "| Health:", main_game_state.castle.boss.health,
                  "| Attack:", main_game_state.castle.boss.attack)

            legal_plays = main_game_state.legalPlays(main_game_state.players[next_turn].hand)

            if len(legal_plays) == 0:
                game_over = True

            print(legal_plays)
            #input("Enter any input to continue:\n")

            root_node.setGameState(deepcopy(main_game_state))
            root_node.setActivePlayer()

            run_count = 0

            # AI stops trying to simulate if it encounters too many dud expansions
            dud_runs = 0
            dud_ratio = 10 # AI stops if dud_runs >= int(run_count/dud_ratio)
            max_duds = int(max_runs/dud_ratio)

            # NOTE - if dud_ratio is too big to return on integer > 0 - default to max_runs
            if max_duds == 0:
                max_duds = max_runs

            current_time = 0
            timer = Timer()
            timer.start()

            print("AI is thinking...\n")

            while run_count < max_runs and current_time < max_time and dud_runs < max_duds:
                selected_node = root_node.Select()

                expanded_node = selected_node.Expand()

                if expanded_node:
                    #print("Simulation Called!")
                    expanded_node.Simulate()
                else:
                    # keep track of how many times the AI tries to expand an end-state node
                    dud_runs += 1

                run_count += 1
                current_time = timer.check()
                #print("Current run count:", run_count)

            # NOTE - log total elapsed time to go run_count
            if time_logging:
                total_time = timer.check()
                logTime(time_logger, max_runs, total_time)

            timer.stop()

            print("Dud Runs: " + str(dud_runs) + " | " + str(round(dud_runs / run_count * 100, 2)) + "% of runs done were duds!")
            print("Total Runs: " + str(run_count) + " | " + str(round(run_count / max_runs * 100, 2)) + "% of requested runs were completed!")

            highest_child = root_node.findHighestRankingChild()
            ai_action = highest_child.getGameAction()

            if ai_action not in legal_plays:
                raise Exception ("AI making illegal move!")

            print("AI's Final Move:", ai_action)
            main_game_state = main_game_state.nextState(ai_action, True)

            # NOTE - turning off state and action log whilst taking timing results
            if action_state_logging:
                logState(state_logger, main_game_state)

            root_node.resetNode()

            state = main_game_state.winner()

            if state == Result.BOSS_DEFEATED:
                boss_defeated += 1
                turns_survived += 1

            elif state == Result.ALIVE:
                turns_survived += 1

            # redundant conditions but kept for readability
            elif state != Result.ALIVE and state != Result.BOSS_DEFEATED:
                game_over = True

    winner = main_game_state.winner()

    if winner == Result.WIN:
        print("ADVENTURERS WIN!", end="\n\n")
        game_over = True
    elif winner == Result.LOSS:
        print("CASTLE WINS!", end="\n\n")
        game_over = True
    # NOTE - This option shouldn't ever be called...
    elif winner == Result.ALIVE:
        print("YOU'RE ALIVE!", end="\n\n")
        game_over = True

    # print game results
    print("Bosses Defeated: " + str(boss_defeated) + " | " + str(round(boss_defeated / 12 * 100, 2)) + "% of castle defeated!", sep="\n")
    print("Turns Survived: " + str(turns_survived) + " | " + str(round(boss_defeated / turns_survived, 2)) + " bosses defeated every turn!", sep="\n")

    # NOTE - turning off state and action log whilst taking timing results
    if action_state_logging:
        logActions(action_logger, main_game_state.actions)

    if result_logging:
        logResults(result_logger, main_game_state, root_node, max_runs, max_time, boss_defeated, turns_survived)

    input("\nPress enter to close application: ")


# input validation
def validPlay(legal_plays):
    valid = False
    play_index = input("Which hand would you like to play (Enter index): ")
    while not valid:
        try:
             if -len(legal_plays) <= int(play_index) < len(legal_plays):
                 play_index = int(play_index)
                 valid = True
             else:
                 play_index = input("Please enter a valid index (Enter index): ")
        except ValueError:
            play_index = input("Please enter a valid (integer) index (Enter index): ")

    return play_index

def validMaxRuns():
    valid = False
    max_runs = input("How many simulation attempts would you like the AI to run?: ")
    while not valid:
        try:
            if 0 <= int(max_runs):
                max_runs = int(max_runs)
                valid = True
            else:
                max_runs = input("Please enter a valid input for maximum runs (Integer > 0): ")
        except ValueError:
            max_runs = input("Please enter a valid input for maximum runs (Integer > 0): ")

    return max_runs

def validMaxTime():
    valid = False
    max_time = input("How many seconds would you like the AI to run?: ")
    while not valid:
        try:
            if 0 <= float(max_time):
                max_time = float(max_time)
                valid = True
            else:
                max_time = input("Please enter a valid input for maximum time (s) (Float > 0): ")
        except ValueError:
            max_time = input("Please enter a valid input for maximum time (s) (Float > 0): ")

    return max_time

# logging functions
def initialiseActionLogger():
    now = datetime.datetime.now()
    now_str = now.strftime("%d%m%y%H%M%S")
    filename = "Logs/Actions/" + now_str + ".log"

    # Create a logger specifically for actions
    logger = logging.getLogger("Actions")
    file_handler = logging.FileHandler(filename, mode="w", encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    logger.info("I log actions! :D")

    return logger

def initialiseStateLogger():
    now = datetime.datetime.now()
    now_str = now.strftime("%d%m%y%H%M%S")
    filename = "Logs/States/" + now_str + ".log"

    # Create a logger specifically for states
    logger = logging.getLogger("States")
    file_handler = logging.FileHandler(filename, mode="w", encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    logger.info("I log states! :D")

    return logger

def initialiseTimeLogger():
    now = datetime.datetime.now()
    now_str = now.strftime("%d%m%y%H%M%S")
    filename = "Logs/Time/" + now_str + ".log"

    # Create a logger specifically for states
    logger = logging.getLogger("Time")
    file_handler = logging.FileHandler(filename, mode="w", encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    logger.info("I log time taken for AI to run max_count! :D")

    return logger

def initialiseResultLogger(name=None):
    now = datetime.datetime.now()

    if not name:
        now_str = now.strftime("%d%m%y%H%M%S")
        filename = "Logs/Results/" + now_str + ".log"

    else:
        filename = "Logs/Results/" + str(name) + ".log"

    # Create a logger specifically for states
    logger = logging.getLogger("Time")
    file_handler = logging.FileHandler(filename, mode="a", encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    #logger.info("I log the results of the game as well as the AI parameters! :D")

    return logger


def logActions(logger, actions):
    for action in actions:
        logger.info("Player: {} | Cards Played: {} | Boss Defeated: {} | Player Died: {}".format(action.marker + 1, action.cards, action.boss_defeated, action.player_died))

def logState(logger, state):
    logger.info("STATE LOG: BEGIN")
    for player in state.players:
        logger.info(player.name + "'s Hand: " + str(player.hand))

    boss = state.castle.boss
    if boss:
        logger.info("Boss: Rank: {} | Suit {} | Attack {} | Health {}".format(boss.rank, boss.suit, boss.attack, boss.health))
    else:
        logger.info("Final Boss Defeated!")

    logger.info("Tavern: " + str(state.tavern.cards))
    logger.info("Castle: " + str(state.castle.cards))
    logger.info("Discard: " + str(state.discard.cards))
    logger.info("Active Player: " + str(state.currentPlayer() + 1))

    logger.info("STATE LOG: END")

def logTime(logger, max_count, time):
    logger.info("Max Count: {} | Time(s): {}".format(max_count, time))

def logResults(logger, state, root_node, max_runs, max_time,boss_defeated, turns_survived):
    logger.info("Max Runs: {} | Max Time: {} | Players {}".format(max_runs, max_time, len(state.players)))
    logger.info("Selection: {} | Expansion: {} | Simulation: {} ".format(root_node.selection_heuristics, root_node.expansion_heuristics, root_node.simulation_heuristics))
    logger.info("Bosses Defeated: {} | {}% of castle defeated".format(str(boss_defeated), str(round(boss_defeated / 12 * 100, 2))))
    logger.info("Turns Survived: {} | {} bosses defeated every turn!".format(str(turns_survived), str(round(boss_defeated / turns_survived, 2))))
    logger.info("-" * 50)


main()
