# REFERENCE - https://realpython.com/python-testing/
# REFERENCE - https://stackoverflow.com/questions/40336601/python-appending-array-to-an-array

# External Imports
import random

# Internal Imports
from Cards.Base.card import Card
from Cards.Regicide.boss import Boss
from Cards.Base.deck import Deck

class Castle(Deck):
    def __init__(self):
        super().__init__()
        self.boss = None

    def create(self):
        if len(self.cards) != 0:
            raise Exception("Castle deck already contains cards!")

        kings = [Boss(rank, suit)
                 for rank in [13] # (13 = K)
                 for suit in ["S", "D", "C", "H"]]

        queens = [Boss(rank, suit)
                 for rank in [12] # (12 = Q)
                 for suit in ["S", "D", "C", "H"]]

        jacks = [Boss(rank, suit)
                  for rank in [11] # (11 = J)
                  for suit in ["S", "D", "C", "H"]]

        random.shuffle(kings)
        random.shuffle(queens)
        random.shuffle(jacks)

        # CONFIG - You can pick and choose what makes up the castle deck - I removed the queens and kings in order to feasible debug the reward system
        self.cards += kings
        self.cards += queens
        self.cards += jacks

    def drawBoss(self):
        if self.boss != None:
            raise Exception("Boss", self.boss, "already in play!")

        if self.cards == None:
            raise Exception("No more cards in castle deck!")

        self.boss = self.cards.pop()

def castle():
    castle = Castle()
    castle.create()
    assert len(castle.cards) == 12, "Castle deck should initially contain 12 cards!"
    castle.drawBoss()
    assert castle.boss.rank == 11, "First boss card should be a Jack!"
    assert len(castle.cards) == 11, "Castle should contain 11 cards after first boss card is drawn!"

if __name__ == "__main__":
    castle()
    print("Everything Passed!")