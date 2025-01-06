class Player:
    # initializer
    def __init__(self, name):
        self.hand = []
        self.name = name

    # setters
    def setHand(self, hand):
        self.hand = hand

    def setName(self, name="John"):
        self.name = name

    # getters
    def getHand(self):
        return self.hand

    def getName(self):
        return self.name

    def __repr__(self):
        return self.name