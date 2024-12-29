# External Imports
from enum import Enum

class RegicideAction:
    def __init__(self, marker, cards, boss_defeated=False, player_died=False):
        self.marker = marker
        self.cards = cards
        self.boss_defeated = boss_defeated
        self.player_died = player_died

    # TODO - create representation of action for debugging
    def __repr__(self):
        return self.marker, "|", self.cards