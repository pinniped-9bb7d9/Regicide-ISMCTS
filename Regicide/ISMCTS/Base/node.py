class Node:
    # setters
    def setGameState(self, new_state, new_action):
        pass

    def setActivePlayer(self):
        pass

    def setParent(self, node):
        pass

    def setDepth(self, depth):
        pass

    # getters
    def getGameState(self):
        pass

    def getGameAction(self):
        pass

    def getRanking(self):
        pass

    # MCTS functions
    def Select(self):
        pass

    def Expand(self):
        pass

    def Simulate(self):
        pass

    def Backpropagate(self, result):
        pass

    # tree functions
    def findHighestRankingChild(self):
        pass

    def calculateResult(self, winner):
        pass

    def resetNode(self):
        pass