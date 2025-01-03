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

def main():
    # CONFIG - Allow the ability to configurate maximum runs and maximum time
    max_runs = validMaxRuns()
    max_time = validMaxTime() # in (s)
    action_state_logging = False
    time_logging = False
    main_game_state = RegicideBoard()
    main_game_state.start()

    # NOTE - turning off state and action log whilst taking timing results
    if action_state_logging:
        action_logger = initialiseActionLogger()
        state_logger = initialiseStateLogger()
        logState(state_logger, main_game_state)

    if time_logging:
        time_logger = initialiseTimeLogger()

    # TODO - Learn how to properly log in Python
    #main_game_state.print_board()
    #print("")

    # TODO - not implemented AI right away - checking gameplay loop works first
    root_node = RegicideNode()

    game_over = False

    while not game_over:

        next_turn = main_game_state.currentPlayer()

        # NOTE - Player is currently set to player 1 - all other players are set to an AI
        if next_turn == 0: # Player's Turn
            print(main_game_state.players[main_game_state.currentPlayer()].name + "'s Turn:")
            legal_plays = main_game_state.legalPlays(main_game_state.players[next_turn].hand)
            print("Boss:", main_game_state.castle.boss, "| Health:", main_game_state.castle.boss.health, "| Attack:",
                  main_game_state.castle.boss.attack)
            print(legal_plays)
            play_index = validPlay(legal_plays)
            print("")
            main_game_state = main_game_state.nextState(legal_plays[play_index])
            # NOTE - turning off state and action log whilst taking timing results
            if action_state_logging:
                logState(state_logger, main_game_state)

            state = main_game_state.winner()

            if state != Result.ALIVE and state != Result.BOSS_DEFEATED:
                game_over = True

        else: # AI's Turn

            print(main_game_state.players[main_game_state.currentPlayer()].name + "'s Turn:")
            print("Boss:", main_game_state.castle.boss, "| Health:", main_game_state.castle.boss.health, "| Attack:",
                  main_game_state.castle.boss.attack)
            legal_plays = main_game_state.legalPlays(main_game_state.players[next_turn].hand)
            print(legal_plays)
            input("Enter any input to continue:\n")

            root_node.setGameState(deepcopy(main_game_state))
            root_node.setActivePlayer()

            run_count = 0
            current_time = 0
            timer = Timer()
            timer.start()

            print("AI is thinking...\n")

            while run_count < max_runs and current_time < max_time:
                # TODO - Fix the recursion within the select function in order to return correctly selected node
                selected_node = root_node.Select()

                expanded_node = selected_node.Expand()

                if expanded_node:
                    # TODO - Learn how to properly log in Python
                    #print("Simulation Called!")
                    expanded_node.Simulate()

                run_count += 1
                current_time = timer.check()
                #print("Current run count:", run_count)

            # NOTE - log total elapsed time to go run_count
            if time_logging:
                total_time = timer.check()
                logTime(time_logger, max_runs, total_time)

            timer.stop()

            highest_child = root_node.findHighestRankingChild()
            ai_action = highest_child.getGameAction()
            print("AI's Final Move:", ai_action)
            print("")
            main_game_state = main_game_state.nextState(ai_action, True)

            # NOTE - turning off state and action log whilst taking timing results
            if action_state_logging:
                logState(state_logger, main_game_state)

            root_node.resetNode()

            state = main_game_state.winner()

            if state != Result.ALIVE and state != Result.BOSS_DEFEATED:
                game_over = True

    winner = main_game_state.winner()

    if winner == Result.WIN:
        print("ADVENTURERS WIN!")
        game_over = True
    elif winner == Result.LOSS:
        print("CASTLE WINS!")
        game_over = True
    # NOTE - This option shouldn't ever be called...
    elif winner == Result.ALIVE:
        print("YOU'RE ALIVE!")
        game_over = True;

    # NOTE - turning off state and action log whilst taking timing results
    if action_state_logging:
        logActions(action_logger, main_game_state.actions)

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

# setting functions
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

def logActions(logger, actions):
    for action in actions:
        logger.info("Player: {} | Cards Played: {} | Boss Defeated: {} | Player Died: {}".format(action.marker + 1, action.cards, action.boss_defeated, action.player_died))

def logState(logger, state):
    logger.info("STATE LOG: BEGIN")
    for player in state.players:
        logger.info(player.name + "'s Hand: " + str(player.hand))

    boss = state.castle.boss
    logger.info("Boss: Rank: {} | Suit {} | Attack {} | Health {}".format(boss.rank, boss.suit, boss.attack, boss.health))

    logger.info("Tavern: " + str(state.tavern.cards))
    logger.info("Castle: " + str(state.castle.cards))
    logger.info("Discard: " + str(state.discard.cards))
    logger.info("Active Player: " + str(state.currentPlayer() + 1))

    logger.info("STATE LOG: END")

def logTime(logger, max_count, time):
    logger.info("Max Count: {} | Time(s): {}".format(max_count, time))

main()
