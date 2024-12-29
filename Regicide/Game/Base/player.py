class Player:
    # initializer
    def __init__(self, name):
        self.hand = []
        self.name = name

    # setters
    def setHand(self, hand: "list of cards") -> None:
        self.hand = hand

    def setName(self, name="John") -> None:
        self.name = name

    # getters
    def getHand(self) -> "list of cards":
        return self.hand

    def getName(self) -> str:
        return self.name

    def __repr__(self):
        return self.name