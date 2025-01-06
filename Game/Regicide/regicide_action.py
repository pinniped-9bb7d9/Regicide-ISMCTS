# External Imports
from enum import Enum

class RegicideAction:
    def __init__(self, marker, cards, boss_defeated=False, player_died=False):
        self.marker = marker
        self.cards = cards

        # NOTE - these values signify the result of the action - used for checking for win conditions and rewarding AI
        self.boss_defeated = boss_defeated
        self.player_died = player_died

    # NOTE - representation of action used for logging
    def __repr__(self):
        return self.marker, "|", self.cards