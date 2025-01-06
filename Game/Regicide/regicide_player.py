# External Imports
import random

# Internal Imports
from Cards.Base.card import Card
from Game.Base.player import Player

class RegicidePlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        # NOTE - recently played cards are stored in a temporary list before being added to the discard pile all at once when a boss is defeated
        self.played = []

    # takes players and returns an integer of their total 'health' based of the sum of the ranks of cards in their hand
    def calculateHealth(self):
        health = 0
        for card in self.hand:
            health += card.rank
        return health

    # checks to see if card to be played is in the player's hand
    def setCardToPlayed(self, card):
        if card not in self.hand:
            raise Exception("Card to be played is not in " + self.name + "'s hand!")

        self.hand.remove(card)
        self.played.append(card)

    # takes player state and total damage to be taken and returns either a false boolean value or list of cards used to defend player
    def takeDamage(self, damage, ai=False):
        if damage < 0:
            raise Exception("Damage taken by player cannot be negative!")

        if damage == 0:
            discarded = []
            return discarded

        if not ai:
            print(self.name + " is taking", damage, "damage!")

        if damage >= self.calculateHealth():
            if not ai:
                print(self.name, "died!")
            return False

        defence = 0
        discarded = []

        if not ai:
            while defence < damage and len(self.hand) > 0:
                print(self.name + "'s hand:", self.hand)

                # TODO - assuming user input is always valid
                index = validPlay(self.hand)
                #index = int(input("Which card do you want to use to defend yourself? (Enter index): "))
                print("")

                card = self.hand[index]
                self.hand.remove(card)
                discarded.append(card)
                defence += card.rank
                damage_left = max(damage - defence, 0)

                if damage_left != 0:
                    print("Damage left to mitigate:", damage_left, "\n")

            if len(self.hand) == 0:
                print(self.name, "died!")
                return False

            return discarded
        else:

            while defence < damage and len(self.hand) > 0:

                if len(self.hand) == 0:
                    # print(self.name, "died!")
                    return False

                # TODO - AI currently just selects a random card in it's hand - prioritise not disposing diamonds or face cards
                non_diamond = [card for card in self.hand if card.suit != "D"]
                face_ranks = ["J", "K", "Q"]
                non_face = [card for card in self.hand if card.rank not in face_ranks]

                selection = self.hand

                if len(non_diamond) != 0 and len(non_face) != 0:
                    selection = [card for card in self.hand if card in non_diamond and card in non_face]

                    # NOTE - if the hand only contains diamonds and face cards - save diamonds
                    if len(selection) == 0:
                        selection = non_diamond

                index = random.randint(0, len(selection) - 1)

                card = selection[index]
                self.hand.remove(card)
                discarded.append(card)
                defence += card.rank


            return discarded

# input validation
# NOTE - used for human player - not AI
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

# testing function
def player():
    player = RegicidePlayer("Noah")

    # test setting the player's hand to be 5 cards
    # TODO - change the Aces rank from 14 to 1
    test_hand = [Card(6, "C"), Card(3, "H"), Card(3, "C"), Card(10, "D"), Card(1, "S")]
    player.setHand(test_hand)
    assert len(player.hand) == 5, "Player hand expected to be set to 5!"

    # test to see if the player takes damage correctly
    test_discard = player.takeDamage(1)
    assert len(test_discard) == 1, "Player should have only discarded one card!"
    assert len(player.hand) == 4, "Player hand expected to be set to 4 now they've taken 1 damage!"

    # test the player taking lots of damage
    test_discard = player.takeDamage(25)
    if not test_discard:
        print(player.name, "died!")

    else:
        assert len(player.hand) > 0, "Player must still have cards in order to be alive..."


if __name__ == "__main__":
    player()
    print("Everything Passed!")