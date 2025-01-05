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

        # CONFIG - heuristic toggle for ease of testing
        self.selection_heuristics = False #UCT
        self.UCT_exploration = 0.7

        self.expansion_heuristics = False
        self.simulation_heuristics = False

    # setters
    def setGameState(self, new_state=None, new_action=None):
        self.game_action = new_action  # action that got us to this state
        self.game_state = new_state

        self.setActivePlayer()

        self.generate_possible_moves(new_state.players[self.active_player].hand)

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
    def Select(self):
        exploration = self.UCT_exploration

        # Prioritise a node if it has no branches
        # Condition has to be 'or'
        # TODO - Optimization could be made to prevent dud selections...
        if len(self.branches) == 0 or len(self.available_moves) > 0:
            return self
        else:
            if not self.selection_heuristics:
                random_branch = random.randint(0, len(self.branches) - 1)
                return self.branches[random_branch].Select()

            # NOTE - UCT Selection - Perhaps not useful/effective due to the simulations of the child branches not being statistically significant...
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
        #self.generate_possible_moves(self.getGameState().players[self.active_player].hand)

        if self.end_state or len(self.available_moves) == 0:
            #raise Exception("Invalid Expand!")
            #print("Trying to expand an end state!")
            return None
        else:
            # print("Not expanding an end-state!")

            # CONFIG - Configuration Options for Expansion Heuristics
            if self.expansion_heuristics:
                move = self.determineExpansionMove(False, True, True, True)
            else:
                move = self.determineExpansionMove(True, False, False, False)

            #print(move)

            self.available_moves.remove(move)

            child_node = RegicideNode()
            child_node.setGameState(deepcopy(self.game_state), deepcopy(move))
            child_node.setParent(self)
            child_node.setDepth(self.depth + 1)

            # NOTE - Band-aid fix - if move isn't a list - turn it into a list
            try:
                length = len(move)
            except TypeError:
                if move:
                    move = [move]

            child_node.game_state.nextState(move, True)

            self.branches.append(child_node)

            return child_node

    def Simulate(self):
        game_state_copy = deepcopy(self.getGameState())
        game_action_copy = deepcopy(self.getGameAction())

        next_turn = self.getGameState().currentPlayer()

        # Determinize
        random_game_state = self.getGameState().cloneAndRandomize(next_turn)

        diamond_check = self.getGameState().diamondCheck()

        winner = self.getGameState().winner()

        boss_bonus = 0
        surviving_turns = 0

        self.end_state = False

        if winner == Result.WIN or winner == Result.LOSS:
            # TODO - band-aid fix - I think the selection algorithm is choosing branches which already are finished game-states so I need to set available branches of that node type to none.
            self.available_moves = []
            self.calculateResult(winner)
            return

        while not self.end_state:
            possible_moves = deepcopy(random_game_state.legalPlays(random_game_state.players[random_game_state.currentPlayer()].hand))

            if len(possible_moves) == 0:
                self.end_state = True
                self.calculateResult(Result.LOSS, 0, 0)
                return

            else:

                if self.simulation_heuristics:
                    move = self.determineSimulationMove(possible_moves, False, True, True, True)
                else:
                    move = self.determineSimulationMove(possible_moves, True, False, False, False)

                # NOTE - Band-aid fix - if move isn't a list - turn it into a list
                try:
                    length = len(move)
                except TypeError:
                    if move:
                        move = [move]

                random_game_state.nextState(move, True)

            winner = random_game_state.winner()

            if winner == Result.ALIVE:
                surviving_turns += 1

            elif winner == Result.BOSS_DEFEATED:
                surviving_turns += 1
                boss_bonus += 1

            # redundant conditions but kept for readability
            elif winner == Result.LOSS or winner == Result.WIN: # i.e not ALIVE or BOSS_DEFEATED
                # OPTIMIZE - if diamond_check is true wouldn't the punishment be so severe that there is no point in continuing simulation?
                self.calculateResult(winner, boss_bonus, surviving_turns, diamond_check)
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
            rank = self.branches[i].getRanking() / (self.branches[i].visits)
            if rank > max_ranking:
                max_ranking = rank
                max_index = i

        return self.branches[max_index]

    def calculateResult(self, winner, boss_bonus = 0, surviving_turns = 0, diamond_check = False):
        # CONFIG - Any end state that results in a win is dramatically prioritised
        reward = 1000000000
        # CONFIG - AI is impartial to losses - only considering  the defeating of bosses
        punishment = 0
        if winner == Result.WIN:
            # CONFIG - Don't need to add boss bonus since reward is so high
            self.Backpropagate(reward)
        elif winner == Result.LOSS:
            # CONFIG - Heavily punish moves that result in instant death or that immediately leave players with no diamonds.
            if (surviving_turns == 0 and self.depth == 1) or (diamond_check and self.depth == 1):
                punishment = -1000000000
                self.Backpropagate(punishment)

            self.Backpropagate(punishment + boss_bonus + surviving_turns)
        return

    def resetNode(self):
        self.branches = []
        self.ranking = 0
        self.visits = 1
        self.depth = 0
        self.available_moves = []

    # heuristic functions
    # NOTE - both determineExpansionMove() and determineSimulationMove() could be abstracted into one method
    def determineExpansionMove(self, random_check = False, combo_check = False, suit_check = False, duplicate_check = False):
        # NOTE - move is default set to first move in list
        move = self.available_moves[0]

        if random_check:
            random_index = random.randint(0, len(self.available_moves) - 1)
            move = self.available_moves[random_index]
            return move

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

        # prioritise heuristic plays first - default to a random move as a redundancy
        if len(moves) > 0:
            random_move = random.randint(0, len(moves) - 1)
            move = moves[random_move]
        else:
            random_move = random.randint(0, len(self.available_moves) - 1)
            move = self.available_moves[random_move]

        return move

    def determineSimulationMove(self, possible_moves, random_check = False, combo_check = False, suit_check = False, duplicate_check = False):
        try:
            move = possible_moves[0]
        except:
            raise Exception('possible_moves is not a list!')

        # NOTE - If random_check is True - all other heuristics are overridden
        if random_check:
            random_index = random.randint(0, len(possible_moves) - 1)
            move = possible_moves[random_index]
            return move

        # turn on combo check if duplicate check is on
        if duplicate_check:
            combo_check = True

        # create list of combos
        combos = []
        if combo_check:
            if len(possible_moves) > 1:
                for move in possible_moves:
                    if move:
                        if len(move) > 1:
                            combos.append(move)

        # create list of moves with suit that isn't the same as the current boss
        other_suit = []
        if suit_check:
            if len(possible_moves) > 1:
                for move in possible_moves:
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
            moves = [move for move in possible_moves if move in combos and move in other_suit]
        elif combo_check:
            moves = combos
        elif suit_check:
            moves = other_suit
        else:
            moves = possible_moves

        # prioritise heuristic plays first - default to a random move as a redundancy
        if len(moves) > 0:
            random_index = random.randint(0, len(moves) - 1)
            move = moves[random_index]
        else:
            random_index = random.randint(0, len(possible_moves) - 1)
            move = possible_moves[random_index]

        return move