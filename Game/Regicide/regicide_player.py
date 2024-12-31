# Internal Imports
from Cards.Base.card import Card
from Game.Base.player import Player

class RegicidePlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.played = []

    def calculateHealth(self) -> int:
        health = 0
        for card in self.hand:
            health += card.rank
        return health

    def setCardToPlayed(self, card):
        if card not in self.hand:
            raise Exception("Card to be played is not in " + self.name + "'s hand!")

        self.hand.remove(card)
        self.played.append(card)

    def takeDamage(self, damage, ai=False): # Return either a false boolean value or list of cards used to defend player
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
                index = int(input("Which card do you want to use to defend yourself? (Enter index): "))
                print("")

                card = self.hand[index]
                self.hand.remove(card)
                discarded.append(card)
                defence += card.rank

                print("Damage left to mitigate:", max(damage - defence, 0))

            if len(self.hand) == 0:
                print(self.name, "died!")
                return False

            return discarded
        else:

            while defence < damage and len(self.hand) > 0:
                # TODO - AI currently just selects the last card in it's hand.
                index = -1

                card = self.hand[index]
                self.hand.remove(card)
                discarded.append(card)
                defence += card.rank

            if len(self.hand) == 0:
                # print(self.name, "died!")
                return False

            return discarded

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