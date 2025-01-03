# External Imports
import random
from copy import deepcopy
from math import sqrt
from math import log
from math import inf

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
        self.visits = 1 #NOTE - visits is set to one when the node is first initialised...
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

        if self.game_state.winner() != Result.ALIVE and self.game_state.winner() != Result.BOSS_DEFEATED:
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
    # REFERENCE - https://github.com/melvinzhang/ismcts/blob/master/ISMCTS.py
    def Select(self, exploration=0.7):
        # CONFIG - Set Selection Heuristic to Sophisticated or Random
        random_select = True

        # Prioritise a node if it has no branches
        # Condition has to be 'or'
        if len(self.branches) == 0 or len(self.available_moves) > 0:
            return self
        else:
            if random_select:
                random_branch = random.randint(0, len(self.branches) - 1)
                return self.branches[random_branch].Select()

            # NOTE - USB1 Selection - Perhaps not useful/effective due to the simulations of the child branches not being statistically significant...
            try:
                rankings = []
                child_index = []
                for child in self.branches:
                    if child.available_moves:
                        rank = float(child.ranking) / float(child.visits) + exploration * sqrt(log(child.parent.visits) / float(child.visits))
                        rankings.append(rank)
                        child_index.append(self.branches.index(child))

                max_rank = max(rankings)
                selection = self.branches[child_index[rankings.index(max_rank)]]

                return selection.Select()
            except ValueError:
                random_branch = random.randint(0, len(self.branches) - 1)
                return self.branches[random_branch].Select()
            except ZeroDivisionError:
                raise Exception("Division by zero!")

    def Expand(self):
        # NOTE - ensure that the function has the correct available_moves
        self.generate_possible_moves(self.getGameState().players[self.active_player].hand)

        if self.end_state or len(self.available_moves) == 0:
            #raise Exception("Invalid Expand!")
            print("Trying to expand an end state!")
            return None
        else:
            # print("Not expanding an end-state!")

            # CONFIG - Configuration Options for Expansion Heuristics
            combo_check = True
            suit_check = True
            duplicate_check = True

            move = self.determineExpansionMove(combo_check, suit_check, duplicate_check)

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

        boss_bonus = 0
        self.end_state = False

        if winner == Result.WIN or winner == Result.LOSS:
            # TODO - band-aid fix - I think the selection algorithm is choosing branches which already are finished game-states so I need to set available branches of that node type to none.
            self.available_moves = []
            self.calculateResult(winner)
            return

        while not self.end_state:
            possible_moves = deepcopy(random_game_state.legalPlays(random_game_state.players[random_game_state.currentPlayer()].hand))

            if len(possible_moves) == 0:
                self.end_state = False
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

            if winner == Result.BOSS_DEFEATED:
                boss_bonus += 1

            if winner == Result.LOSS or winner == Result.WIN: # i.e not ALIVE or BOSS_DEFEATED
                self.calculateResult(winner, boss_bonus)
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

        max_ranking = -inf
        max_index = 0

        for i in range(len(self.branches)):
            self.rank = self.branches[i].getRanking() / (self.branches[i].visits)
            if self.rank > max_ranking:
                max_ranking = self.rank
                max_index = i

        return self.branches[max_index]

    def calculateResult(self, winner, boss_bonus = 0):
        # CONFIG - Any end state that results in a win is dramatically prioritised
        reward = 1000000000
        # CONFIG - AI is impartial to losses - only considering  the defeating of bosses
        punishment = 0
        if winner == Result.WIN:
            # CONFIG - Don't need to add boss bonus since reward is so high
            self.Backpropagate(reward)
        elif winner == Result.LOSS:
            self.Backpropagate(punishment + boss_bonus)
        return

    def resetNode(self):
        self.branches = []
        self.ranking = 0
        self.visits = 1
        self.depth = 0
        self.available_moves = []

    # heuristic functions
    def determineExpansionMove(self, combo_check = False, suit_check = False, duplicate_check = False):
        # NOTE - move is default set to first move in list
        move = self.available_moves[0]

        # turn on combo check if duplicate check is on
        if duplicate_check:
            combo_check = True

        # create list of combos
        combos = []
        if combo_check:
            if len(self.available_moves) > 1:
                for move in self.available_moves:
                    if move:
                        if len(move) > 1:
                            combos.append(move)

        # create list of moves with suit that isn't the same as the current boss
        other_suit = []
        if suit_check:
            if len(self.available_moves) > 1:
                for move in self.available_moves:
                    if move:
                        other_suit_check = True
                        for card in move:
                            if card.suit == self.game_state.castle.boss.suit:
                                other_suit_check = False
                        if other_suit_check:
                            other_suit.append(move)

        # create list of combos that don't have duplicate suit types
        # NOTE - edits already made combo list
        duplicates = []
        if duplicate_check:
            for move in combos:
                duplicate = False
                for card in move:
                    move_copy = deepcopy(move)
                    move_copy.remove(card)
                    for other_card in move_copy:
                        if card.suit == other_card.suit and card.suit != other_card.suit:
                            duplicate = True
                if duplicate:
                    duplicates.append(move)

            combos = [move for move in combos if move not in duplicates]

        # combine lists if multiple checks are on
        if suit_check and combo_check:
            moves = [move for move in self.available_moves if move in combos and move in other_suit]
        elif combo_check:
            moves = combos
        elif suit_check:
            moves = other_suit
        else:
            moves = self.available_moves

        # prioritise combos first
        if len(moves) > 0:
            random_move = random.randint(0, len(moves) - 1)
            move = combos[random_move]
        else:
            random_move = random.randint(0, len(self.available_moves) - 1)
            move = self.available_moves[random_move]

        return move