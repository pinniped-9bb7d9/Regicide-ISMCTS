# External Imports
import random
from copy import deepcopy

from Game.Regicide.regicide_action import RegicideAction
# Internal Imports
from ISMCTS.Base.node import Node
from Game.Regicide.regicide_board import Result

class RegicideNode(Node):
    def __init__(self):
        self.end_state = False
        self.game_state = None
        self.game_action = None
        self.result = None
        self.parent = None
        self.active_player = None
        self.ranking = 0
        self.depth = 0
        self.visits = 0
        self.available_moves = []
        self.branches = []
        self.rank = 0

    # setters
    def setGameState(self, new_state=None, new_action=None):
        self.game_action = new_action  # action that got us to this state
        self.game_state = new_state

        marker = new_state.currentPlayer()

        self.generate_possible_moves(new_state.players[marker].hand)

    def setActivePlayer(self):
        self.active_player = self.game_state.currentPlayer()

    def setParent(self, node):
        self.parent = node

    def setDepth(self, depth):
        self.depth = depth

    def generate_possible_moves(self, cards=None):
        self.available_moves = self.game_state.legalPlays(cards)

        if len(self.available_moves) == 0:
            self.end_state = True

        if self.game_state.winner() != Result.ALIVE:
            self.end_state = True

    # getters
    # NOTE - All these getters are redundant since variables in node are not set to private
    def getGameState(self):
        return self.game_state

    def getGameAction(self):
        return self.game_action

    def getRanking(self):
        return self.ranking

    # MCTS functions
    def Select(self):
        if len(self.branches) == 0 or len(self.available_moves) > 0:
            return self
        else:
            # TODO - add sophisticated selection heuristics
            random_branch = random.randint(0, len(self.branches) - 1)
            return self.branches[random_branch].Select()

    def Expand(self):
        #self.generate_possible_moves(self.getGameState().players[self.active_player].hand)

        if self.end_state or len(self.available_moves) == 0:
            #raise Exception("Invalid Expand!")
            return None
        else:

            random_move = random.randint(0, len(self.available_moves) - 1)
            move = self.available_moves[random_move]

            self.available_moves.remove(move)

            child_node = deepcopy(self)
            child_node.branches = []
            child_node.setParent(self)
            child_node.setDepth(self.depth + 1)

            new_game_state = deepcopy(self.game_state)

            # NOTE - Band-aid fix - if move isn't a list - turn it into a list
            try:
                length = len(move)
            except TypeError:
                if move:
                    move = [move]

            new_game_state.nextState(move, True)

            child_node.game_state = new_game_state
            child_node.game_action = move

            self.branches.append(child_node)

            return child_node

    def Simulate(self):
        # TODO - Create simulation function...
        game_state_copy = deepcopy(self.getGameState())
        game_action_copy = deepcopy(self.getGameAction())

        next_turn = self.getGameState().currentPlayer()
        random_game_state = self.getGameState().cloneAndRandomize(next_turn)

        winner = self.getGameState().winner()

        self.end_state = False

        if winner != Result.ALIVE:
            # TODO - band-aid fix - I think the selection algorithm is choosing branches which already are finished game-states so I need to set available branches of that node type to none.
            self.available_moves = []
            self.calculateResult(winner)
            return

        while not self.end_state:
            possible_moves = deepcopy(random_game_state.legalPlays(random_game_state.players[random_game_state.currentPlayer()].hand))

            if len(possible_moves) == 0:
                self.end_state = True
                self.calculateResult(Result.LOSS)
                return

            else:
                random_move = random.randint(0, len(possible_moves) - 1)
                move = possible_moves[random_move]

                # NOTE - Band-aid fix - if move isn't a list - turn it into a list
                try:
                    length = len(move)
                except TypeError:
                    if move:
                        move = [move]

                random_game_state.nextState(move, True)

            winner = random_game_state.winner()

            if winner != Result.ALIVE:
                self.calculateResult(winner)
                self.end_state = False
                self.setGameState(game_state_copy, game_action_copy)
                return

    def Backpropagate(self, result):
        self.ranking += result
        self.visits += 1

        if self.parent:
            self.parent.Backpropagate(result)

    # tree functions
    def findHighestRankingChild(self):
        if not self.branches:
            raise Exception("Error: 'findHighestRankingChild()' called without a branch list!")

        max_ranking = -1000.0
        max_index = 0

        for i in range(len(self.branches)):
            self.rank = self.branches[i].getRanking() / (self.branches[i].depth + 1)
            if self.rank > max_ranking:
                max_ranking = self.rank
                max_index = i

        return self.branches[max_index]

    def calculateResult(self, winner):
        if winner == Result.WIN:
            self.Backpropagate(1)
        elif winner == Result.LOSS:
            self.Backpropagate(-1)
        return

    def resetNode(self):
        self.branches = []
        self.ranking = 0
        self.visits = 0
        self.depth = 0
        self.available_moves = []