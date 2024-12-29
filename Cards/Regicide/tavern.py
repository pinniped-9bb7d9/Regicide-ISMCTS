# External Imports
import random

# Internal Imports
from Cards.Base.card import Card
from Cards.Base.deck import Deck
from Cards.Regicide.boss import Boss

class Tavern(Deck):
    def __init__(self):
        super().__init__()

    def create(self):
        self.cards = [Card(rank, suit)
                      for rank in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                      for suit in ["C", "D", "H", "S"]]
        self.boss = []

        random.shuffle(self.cards)

    def drawCard(self):
        if len(self.boss) != 0:
            return self.boss.pop()
        return self.cards.pop()

    def addCards(self, cards):
        if len(cards) == 0:
            raise Exception("No cards to add!")

        # TODO - If a round ends with a boss on the top of the deck - does the boss stay there?
        self.cards += cards

    def addBoss(self, boss):
        if boss.rank not in [11, 12, 13]:
            raise Exception("Card must be a boss to placed on top of the tavern deck!")

        self.boss.append(Card(boss.rank, boss.suit))

def tavern():
    tavern = Tavern()

    # test initializing the tavern deck
    tavern.create()
    assert len(tavern.cards) == 40, "Tavern deck should initially contain 40 cards!"
    for card in tavern.cards:
        assert card.rank < 11, "No face cards should initially be in the tavern deck!"

    # test drawing a card
    test_draw = tavern.drawCard()
    assert test_draw, "There should be one card drawn!"
    assert len(tavern.cards) == 39, "Tavern deck should have one less card!"

    # test adding drawn card back in the deck
    test_pile = [test_draw]
    tavern.addCards(test_pile)
    assert len(tavern.cards) == 40, "Tavern deck should now be back up to 40 cards!"

    # test adding a boss to the 'top' of the deck
    test_boss = Boss(12, "H") # Queen of Hearts
    tavern.addBoss(test_boss)
    assert tavern.boss, "Tavern deck should now contain a boss card!"

    # test drawing the deck whilst there is a boss card
    test_draw_boss = tavern.drawCard()
    assert test_draw_boss == Card(12, "H"), "Drawn card should be the Queen of Hearts!"
    assert len(tavern.boss) == 0, "Tavern deck shouldn't have any boss cards!"
    assert len(tavern.cards) == 40, "Tavern deck should still contain 40 cards!"

if __name__ == "__main__":
    tavern()
    print("Everything Passed!")

