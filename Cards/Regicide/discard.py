# Internal Imports
from Cards.Base.card import Card
from Cards.Base.deck import Deck

# simple discard pile that can have cards drawn and added

class Discard(Deck):
    def __init__(self):
        super().__init__()

    # need to override create() in order to not have it take the create() from Deck
    def create(self):
        self.cards = []

    def drawCard(self):
        if len(self.cards) == 0:
            raise Exception("No cards to draw!")
        return self.cards.pop()

    def addCards(self, cards):
        if len(cards) == 0:
            raise Exception("No cards to add!")
        self.cards += cards

def discard():
    discard = Discard()

    # test initializing the discard pile
    discard.create()
    assert len(discard.cards) == 0, "Discard pile should be empty!"

    # add a mock list of cards to the discard pile
    test_cards = [Card(5, "H"), Card(13, "S"), Card(7, "H")]
    discard.addCards(test_cards)
    assert len(discard.cards) == len(test_cards), "Discard pile should be the same size as the test list!"

    # test drawing a card from the discard pile
    test_draw = discard.drawCard()
    assert test_draw == test_cards[-1], "Incorrect card has been drawn from the discard pile!"

if __name__ == "__main__":
    discard()
    print("Everything Passed!")