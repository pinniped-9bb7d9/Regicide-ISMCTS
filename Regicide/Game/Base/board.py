# REFERENCE - https://jeffbradberry.com/posts/2015/09/intro-to-monte-carlo-tree-search/

class Board:
    def start(self):
        # Returns a representation of the starting state of the game.
        pass

    def currentPlayer(self):
        # Takes the game state and returns the current player's
        # number.
        pass

    def nextState(self, play):
        # Takes the game state, and the move to be applied.
        # Returns the new game state.
        pass

    def legalPlays(self, cards):
        # Takes a sequence of game states representing the full
        # game history, and returns the full list of moves that
        # are legal plays for the current player.
        pass

    def winner(self, action):
        # Takes a sequence of game states representing the full
        # game history.  If the game is now won, return the player
        # number.  If the game is still ongoing, return zero.  If
        # the game is tied, return a different distinct value, e.g. -1.
        pass