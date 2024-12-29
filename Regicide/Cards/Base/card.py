# REFERENCE - https://github.com/melvinzhang/ismcts/blob/master/ISMCTS.py
# REFERENCE - https://www.geeksforgeeks.org/dunder-magic-methods-python/
# REFERENCE - https://www.datacamp.com/tutorial/python-list-index
# REFERENCE - https://stackoverflow.com/questions/3501382/checking-whether-a-variable-is-an-integer-or-not

# External Imports
import random

class Card:
    """ A playing card, with rank and suit.
        rank must be an integer between 2 and 14 inclusive (Jack=11, Queen=12, King=13, Ace=14)
        suit must be a string of length 1, one of 'C' (Clubs), 'D' (Diamonds), 'H' (Hearts) or 'S' (Spades)
    """

    def __init__(self, rank, suit):
        # convert rank from string to integer index - except not if it's already an integer
        try:
            rank = "??23456789TJQKA".index(rank)
        except TypeError:
            pass

        # TODO - input validation can only be done outside of '__init__()'
        if rank not in list(range(1, 13 + 1)):
            raise Exception("Invalid rank")
        if suit not in ["C", "D", "H", "S"]:
            raise Exception("Invalid suit")
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return "?A23456789TJQK"[self.rank] + self.suit

    def __eq__(self, other):
        # TODO - AttributeError if last move available is None
        return self.rank == other.rank and self.suit == other.suit

    def __ne__(self, other):
        return self.rank != other.rank or self.suit != other.suit

    def __lt__(self, other):
        if self.rank == other.rank:
            return self.suit < other.suit

        return self.rank < other.rank

    def __gt__(self, other):
        if self.suit == other.suit:
            return self.rank > other.rank

        return self.suit > other.suit