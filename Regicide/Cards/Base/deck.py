# REFERENCE - https://github.com/melvinzhang/ismcts/blob/master/ISMCTS.py
# REFERENCE - https://www.geeksforgeeks.org/dunder-magic-methods-python/
# REFERENCE - https://www.datacamp.com/tutorial/python-list-index
# REFERENCE - https://stackoverflow.com/questions/3501382/checking-whether-a-variable-is-an-integer-or-not

# External Imports
import random

# Internal Imports
from Cards.Base.card import Card

class Deck:
    def __init__(self):
        self.cards = []

    # create a standard 52-card deck
    def create(self):
        self.cards = [Card(rank, suit)
                      for rank in range(1, 13 + 1)
                      for suit in ["C", "D", "H", "S"]]

        return self.cards

    def shuffle(self):
        random.shuffle(self.cards)

    def split(self):
        first_half = self.cards[:len(self.cards) // 2]
        second_half = self.cards[len(self.cards) // 2:]
        return first_half, second_half