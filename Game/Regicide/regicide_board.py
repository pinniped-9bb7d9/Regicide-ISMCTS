# External Imports
from copy import deepcopy
from enum import Enum
import random
import logging

# Internal Imports
from Game.Base.board import Board
from Cards.Base.card import Card
from Cards.Base.deck import Deck
from Game.Regicide.regicide_player import RegicidePlayer
from Game.Regicide.regicide_action import RegicideAction
from Cards.Regicide.castle import Castle
from Cards.Regicide.tavern import Tavern
from Cards.Regicide.discard import Discard

class RegicideBoard(Board):
    def __init__(self):
        self.players = []
        self.discard = Discard()
        self.castle = Castle()
        self.tavern = Tavern()
        self.powers = [] # stores suit powers in the form of a character array (["H", "S"])
        self.actions = []
        self.hand_size = 0
        self.consecutive_yields = 0
        self.verbose = False # NOTE - if verbose is set to true - extensive logging on what exactly is happening to terminal

        if self.verbose:
            # REFERENCE - https://realpython.com/python-logging/#adjusting-the-log-level
            logging.basicConfig(
                format="\n%(asctime)s - %(levelname)s - %(message)s",
                style="%",
                datefmt="%Y-%m-%d %H:%M",
                level=logging.INFO
            )

    # def __repr__(self):
    #     return str(len(self.players))

    def start(self):
        # TODO - input validation
        valid = False
        num_players = input("How many players would you like to have play? (2-4): ")
        while not valid:
            try:
                if int(num_players) in [2, 3, 4]:
                    num_players = int(num_players)
                    valid = True
                else:
                    num_players = input("Please enter an appropriate amount of players... (2-4): ")
            except ValueError:
                num_players = input("Please enter an appropriate amount (integer) of players... (2-4): ")
        print()

        for counter in range(num_players):
            name = input("What is Player " + str(counter + 1) + "'s name?: ")
            player = RegicidePlayer(name)
            self.players.append(player)

        self.discard.create()
        self.castle.create()
        self.tavern.create()

        self.hand_size = int("??765"[num_players])

        for player in self.players:
            for counter in range(self.hand_size):
                player.hand.append(self.tavern.drawCard())

        self.castle.drawBoss()

        if self.verbose:
            self.logBoard()

    def currentPlayer(self):
        # it's player 1's turn (index 0) when game first begins
        if len(self.actions) == 0:
            return 0

        last_action = self.actions[-1]

        if last_action.boss_defeated:
            return last_action.marker

        last_player = last_action.marker
        next_player = (last_player + 1) % len(self.players)

        return next_player

    # NOTE - 'play' is currently optional for debugging
    def nextState(self, play=None, ai=False, final=False):
        # FIXME - This is the problem line of code...
        current_player = self.currentPlayer()

        # FIXME - Instead of calculating current player based on history of actions - base it of on which hand contains the cards in play?

        boss_defeated = False
        player_died = False


        if not play:
            self.consecutive_yields += 1

            # NOTE - if player yields - they immediately take damage from the boss
            discarded = self.players[current_player].takeDamage(self.castle.boss.attack, ai)

            if not discarded and self.castle.boss.attack != 0:
                player_died = True
            else:
                if len(discarded) != 0:
                    self.discard.addCards(deepcopy(discarded))

            action = RegicideAction(current_player, play, boss_defeated, player_died)
            self.actions.append(action)
            return self

        # Set cards to played first to check its a valid move before applying card effects
        for card in play:
            self.players[current_player].setCardToPlayed(card)

        self.consecutive_yields = 0

        try:
            perfect_hit = self.castle.boss.cardEffect(play)
        except AttributeError:
            raise Exception("Trying to cardEffect() a NoneType boss!")
        if not ai or final:
            self.cardEffect(play)
        else:
            self.cardEffect(play, True)

        # TEST - If player defeats the boss - put all the cards the played into the discard pile have the same player start the next phase
        # NOTE - perfect hit adding current boss to tavern deck isn't currently implemented
        if self.castle.boss.health == 0:
            if not ai or final:
                print("Boss Defeated!")
            for player in self.players:
                if len(player.played) != 0:
                    if not ai or final:
                        print(player.name + "'s Played Cards added to Discard Pile:", player.played)
                    self.discard.addCards(deepcopy(player.played))
                player.played = []
            if perfect_hit:
                if not ai or final:
                    print("Perfect Hit!")
                self.tavern.addBoss(self.castle.boss)
            else:
                self.discard.addCards([deepcopy(self.castle.boss)])
            self.castle.boss = None
            boss_defeated = True

            if len(self.castle.cards) != 0:
                self.castle.drawBoss()
        else:
            discarded = self.players[current_player].takeDamage(self.castle.boss.attack, ai)

            if not discarded and self.castle.boss.attack != 0:
                player_died = True
            else:
                if len(discarded) != 0:
                    # TEMP - print for testing
                    if not ai or final:
                        print("Discarded Defence:", discarded)
                    self.discard.addCards(deepcopy(discarded))

        action = RegicideAction(current_player, play, boss_defeated, player_died)
        self.actions.append(action)

        # NOTE - display piles as game progresses...
        if self.verbose and not ai:
            self.logBoard()

        return self

    def legalPlays(self, cards=None):
        legal_plays = []
        cards.sort()

        # return hand if player only has one card
        if len(cards) == 1:
            if self.consecutive_yields < len(self.players) - 1:
                return [cards] + [None]
            return [cards]

        # first simply append each card on their own
        for card in cards:
            if [card] not in legal_plays: # don't duplicate possible hands
                legal_plays.append([card])

        # now check any of the cards are animal companions and - if so - have legal plays for animal pair companions
        for card in cards:
            # TODO - change ace rank from 14 to 1
            if card.rank == 1:
                cards_copy = deepcopy(cards)
                cards_copy.remove(card)
                for companion in cards_copy:
                    if companion.rank != 1:
                        animal_combo = [card, companion]
                        # TODO - slightly inefficient since it brute forces checking for duplicates - my intuition says there is a more eloquent solution...
                        if animal_combo not in legal_plays:
                            legal_plays.append(animal_combo)

        # now check for combos of two
        two_combos = []
        for card in cards:
            if card.rank in [2, 3, 4, 5]:
                cards_copy = deepcopy(cards)
                cards_copy.remove(card)
                combo = [card]
                for combo_card in cards_copy:
                    if card.rank == combo_card.rank:
                        combo = [card, combo_card]
                        combo.sort()
                        # TODO - see previous todo
                        if combo not in two_combos:
                            two_combos.append(deepcopy(combo))

        # take combos of two and check for combos of three
        three_combos = []
        if len(two_combos) != 0:
            legal_plays += two_combos
            for combo in two_combos:
                for card in cards:
                    if card.rank in [2, 3] and card.rank == combo[0].rank and card not in combo:
                        three_combo = deepcopy(combo) + [card]
                        three_combo.sort()
                        if three_combo not in three_combos:
                            three_combos.append(three_combo)

        # take combos of three and check for combos of four (we can return this the second we find one since it's only possible to have one combo of four)
        four_combo = []
        if len(three_combos) != 0:
            legal_plays += three_combos
            for combo in three_combos:
                if len(four_combo) == 0:
                    for card in cards:
                        if card.rank == 2 and card.rank == combo[0].rank and card not in combo:
                            four_combo = deepcopy(combo) + [card]
                            legal_plays += [four_combo]

        # return an extra 'None' type is for yielding
        # NOTE - you can't yield if every other player before you has also yielded
        if self.consecutive_yields < len(self.players) - 1:
            return legal_plays + [None]

        return legal_plays

    def winner(self, last_action=None):
        # NOTE - Boss Reward Check Parameter
        boss_condition = True

        try:
            if not last_action:
                last_action = self.actions[-1]
        except IndexError:
            return Result.ALIVE # Game just started

        result = Result.ALIVE

        if last_action.player_died:
            result = Result.LOSS

        # NOTE - band-aid - redundant check of player hands in case of error
        for player in self.players:
            if self.castle.boss:
                if len(player.hand) == 0 and self.castle.boss.attack != 0:
                    result = Result.LOSS

        if boss_condition:
            if last_action.boss_defeated:
                result = Result.BOSS_DEFEATED

        if last_action.boss_defeated and len(self.castle.cards) == 0 and not self.castle.boss:
            result = Result.WIN

        return result

    def cardEffect(self, cards, ai = False):

        try:
            length = len(cards)
        except TypeError:
           if cards:
               cards = [cards]

        heart_check = False
        diamond_check = False
        boss_suit = self.castle.boss.suit
        power = 0
        for card in cards:
            power += card.rank
            if card.suit == "H" and boss_suit != "H":
                heart_check = True
            if card.suit == "D" and boss_suit != "D":
                diamond_check = True

        if heart_check:
            self.applyHeart(power, ai)

        if diamond_check:
            self.applyDaimond(power, ai)

    # NOTE - spade and clubs effects are written in the Boss class since they only apply to the current boss and not the current game state
    def applyHeart(self, power, ai = False):
        if len(self.discard.cards) != 0:
            random.shuffle(self.discard.cards)
            counter = 0
            drawn_cards = []
            while counter < power and len(self.discard.cards) != 0:
                card = self.discard.drawCard()
                drawn_cards.append(card)
                counter += 1

            # TEMP - print for testing
            if not ai:
                print("Cards being moved from the discard to tavern deck:", drawn_cards)
            self.tavern.cards = drawn_cards + self.tavern.cards

    def applyDaimond(self, power, ai = False):
        current_player = self.currentPlayer()
        counter = 0
        full = set([])
        while counter < power and (len(self.tavern.cards) != 0 or len(self.tavern.boss) != 0) and len(full) < len(self.players):
            if len(self.players[current_player].hand) < self.hand_size:
                # TEMP - print for testing
                if not ai:
                    print(self.players[current_player].name + " is drawing a card from the Tavern!")
                drawn_card = self.tavern.drawCard()
                self.players[current_player].hand.append(drawn_card)
                counter += 1
            else:
                # TEMP - print for testing
                if not ai:
                    print(self.players[current_player].name + " has a full hand!")
                full.add(self.players[current_player])
            current_player = (current_player + 1) % len(self.players)

    # REFERENCE - https://github.com/melvinzhang/ismcts/blob/master/ISMCTS.py (GameState.CloneAndRandomize())
    def cloneAndRandomize(self, marker=None):

        # NOTE - usually self determine current player but have the optional parameter for ease of debugging
        if not marker:
            marker = self.currentPlayer()

        state = deepcopy(self)

        seen_cards = []
        # current player can see/know:
        ## their own hand
        ## boss cards on top of the tavern
        ## cards in the discard pile
        ## the current castle boss
        ## the remaining cards in the castle (just not in what order)
        seen_cards += state.players[marker].hand if len(state.players[marker].hand) != 0 else []
        seen_cards += state.tavern.boss if len(state.tavern.boss) != 0 else []
        seen_cards += state.discard.cards if len(state.discard.cards) != 0 else []
        seen_cards += [state.castle.boss] if state.castle.boss else []
        seen_cards += state.castle.cards if len(state.castle.cards) != 0 else []

        unseen_cards = [card for card in Deck().create() if card not in seen_cards]

        random.shuffle(unseen_cards)

        # assign cards back into tavern deck
        num_cards = len(state.tavern.cards)
        state.tavern.cards = unseen_cards[:num_cards]
        unseen_cards = unseen_cards[num_cards:]

        # assign cards back into players hand's
        for player in range(0, len(self.players)):
            if player != marker:
                num_cards = len(state.players[player].hand)
                state.players[player].hand = unseen_cards[:num_cards]
                unseen_cards = unseen_cards[num_cards:]

        # shuffle castle deck back together
        castle = state.castle.cards if len(state.castle.cards) != 0 else None

        if castle:
            random.shuffle(castle)
            castle.sort(reverse=True)
            state.castle.cards = castle

        return state

    # print lengths of each players hand to the terminal
    def displayHandLengths(self):
        if len(self.players) < 2:
            raise Exception ("Invalid call to displayHandLengths()! - Invalid amount of players!")

        string = "Hand Sizes - "
        for player in self.players:
            string += (player.name + " - " + str(len(player.hand)))
            if player != self.players[-1]:
                string += " | "

        print(string)

    def diamondCheck(self, hands=None):
        if not hands:
            hands = []
            for player in self.players:
                hands.append(player.hand)

        # flatten cards in player hands into one list
        # REFERENCE - https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists
        cards_in_hands = [card for hand in hands for card in hand]

        # check for diamond
        diamonds = [card for card in cards_in_hands if card.suit == "D"]

        if len(diamonds) != 0:
            return False
        else:
            return True


    # logging functions
    def logBoard(self):
        # NOTE - show player's hands
        for player in self.players:
            logging.info("Player=%s | Hand=%s | Played=%s", player.name, player.hand, player.played)

        logging.info("Castle=%s", self.castle.cards)
        logging.info("Boss=%s | Attack=%s | Health=%s", self.castle.boss, self.castle.boss.attack, self.castle.boss.health)
        logging.info("Tavern=%s", self.tavern.cards)
        logging.info("Discard=%s", self.discard.cards)

class Result(Enum):
    ALIVE = 0
    WIN = 1
    LOSS = 2
    BOSS_DEFEATED = 3

# utitily function
def sumOfRanks(cards):
    total = 0
    for card in cards:
        total += card.rank
    return total

# testing functions
def board():
    board = RegicideBoard()

    # test a normal hand of five random cards
    test_hand = [Card(2, "S"), Card(13, "H"), Card(3, "D"), Card(5, "D"), Card(9, "C")]
    legal_plays = board.legalPlays(test_hand)
    assert len(legal_plays) == 5, "Test hand of five cards of unique rank with no aces should have 6 legal moves!"

    # test a hand of four 2's
    test_hand = [Card(2, "H"), Card(2, "S"), Card(2, "D"), Card(2, "C")]
    legal_plays = board.legalPlays(test_hand)
    assert len(legal_plays) == 15, "Test hand of four 2's should have 16 legal moves!"

    # test animal companion hand with combos
    test_hand = [Card(2, "H"), Card(3, "H"), Card(13, "S"), Card(1, "H"), Card(3, "S"), Card(3, "D")]
    legal_plays = board.legalPlays(test_hand)
    assert len(legal_plays) == 15, "Given test hand should have 16 legal moves!"

    # test multiple animal companion hand with combos
    test_hand = [Card(2, "H"), Card(1, "S"), Card(13, "S"), Card(1, "H"), Card(3, "S"), Card(3, "D")]
    legal_plays = board.legalPlays(test_hand)
    assert len(legal_plays) == 15, "Given test hand should have 16 legal moves!"

    test_index = int(input("What test do you want to do? (0 - Game) (1 - CLone & Randomize): "))

    # Test the board starting up and taking two turns
    if test_index == 0:
        board.start()
        game_over = False
        while not game_over:
            print("")
            print(board.players[board.currentPlayer()].name + "'s Turn:")
            legal_plays = board.legalPlays(board.players[board.currentPlayer()].hand)
            print("Boss:", board.castle.boss, "| Health:", board.castle.boss.health, "| Attack:", board.castle.boss.attack)
            print(legal_plays)
            play_index = int(input("Which hand would you like to play (Enter index): "))
            print("")
            board = board.nextState(legal_plays[play_index])

            state = board.winner()

            if state != Result.ALIVE:
                game_over = True

        print("Game Over!")

    elif test_index == 1:
        board.start()
        clone = board.cloneAndRandomize(random.randint(0, len(board.players) - 1))
        print(clone)


    # assert len(board.actions) == 1, "Board should have one actions logged."
    # print("")
    # current_player = board.currentPlayer()
    # print(board.players[current_player].name + "'s Turn:")
    # legal_plays = board.legalPlays(board.players[current_player].hand)
    # print("Boss:", board.castle.boss, "| Health:", board.castle.boss.health, "| Attack:", board.castle.boss.attack)
    # print(legal_plays)
    # play_index = int(input("Which hand would you like to play (Enter index): "))
    # print("")
    #
    # board.nextState(legal_plays[play_index])
    # # board.nextState(legal_plays[1])
    # print("")
    # print(board.players[board.currentPlayer()].name + "'s Turn: ...")

if __name__ == "__main__":
    board()
    print("Everything Passed!")