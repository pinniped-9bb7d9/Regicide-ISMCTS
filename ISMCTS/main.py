# External Imports
from copy import deepcopy

# Internal Imports
from Game.Regicide.regicide_board import Result
from Game.Regicide.regicide_action import RegicideAction
from Game.Regicide.regicide_board import RegicideBoard
from ISMCTS.Game.regicide_node import RegicideNode
from ISMCTS.Base.timer import Timer

def main():
    max_runs = 100
    max_time = 1
    main_game_state = RegicideBoard()
    main_game_state.start()

    # TODO - Learn how to properly log in Python
    #main_game_state.print_board()
    #print("")

    # TODO - not implemented AI right away - checking gameplay loop works first
    root_node = RegicideNode()

    game_over = False

    while not game_over:

        next_turn = main_game_state.currentPlayer()

        # TODO - Player is currently set to player 1 - all other players are set to an AI
        if next_turn == 0: # Player's Turn
            print(main_game_state.players[main_game_state.currentPlayer()].name + "'s Turn:")
            legal_plays = main_game_state.legalPlays(main_game_state.players[next_turn].hand)
            print("Boss:", main_game_state.castle.boss, "| Health:", main_game_state.castle.boss.health, "| Attack:",
                  main_game_state.castle.boss.attack)
            print(legal_plays)
            play_index = int(input("Which hand would you like to play (Enter index): "))
            print("")
            main_game_state = main_game_state.nextState(legal_plays[play_index])

            state = main_game_state.winner()

            if state != Result.ALIVE and state != Result.BOSS_DEFEATED:
                game_over = True

        else: # AI's Turn

            print("AI is thinking...")
            print(main_game_state.players[main_game_state.currentPlayer()].name + "'s Turn:")
            print("Boss:", main_game_state.castle.boss, "| Health:", main_game_state.castle.boss.health, "| Attack:",
                  main_game_state.castle.boss.attack)
            legal_plays = main_game_state.legalPlays(main_game_state.players[next_turn].hand)
            print(legal_plays)
            input()

            root_node.setGameState(deepcopy(main_game_state))
            root_node.setActivePlayer()

            run_count = 0
            current_time = 0
            timer = Timer()
            timer.start()

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
                # print("Current run count:", run_count)

            highest_child = root_node.findHighestRankingChild()
            ai_action = highest_child.getGameAction()
            print("AI's Final Move:", ai_action)
            print("")
            main_game_state = main_game_state.nextState(ai_action, True)

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


main()
