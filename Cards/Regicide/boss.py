# Internal Imports
from Cards.Base.card import Card

# Boss is a special type of card that are used to make up the tavern deck in a game of Regicide.
# They are converted into normal cards once they are put into the tavern deck or discard pile.
class Boss(Card):
    def __init__(self, rank, suit):
        super().__init__(rank, suit)

        # set damage and health values based on cards rank
        # J = 11, Q = 12, K = 13

        if self.rank == 11:
            self.attack = 10
            self.health = 20
        elif self.rank == 12:
            self.attack = 15
            self.health = 30
        elif self.rank == 13:
            self.attack = 20
            self.health = 40
        else:
            raise Exception("Invalid Boss Rank!")

    def cardEffect(self, cards):

        try:
            length = len(cards)
        except TypeError:
           if cards:
               cards = [cards]

        club_check = False
        spades_check = False
        damage = 0;
        for card in cards:
            # TODO - this makes having 'sumOfRanks()' wee bit redundant but isn't an issue
            damage += card.rank
            if card.suit == "C" and self.suit != "C":
                club_check = True
            if card.suit == "S" and self.suit != "S":
                spades_check = True

        # NOTE - in which order do the club and spades suit powers apply?
        # NOTE - for now, I will have it so if a combo is played
        # take away attack power from boss if the spades suit power applies
        if spades_check:
            self.attack = max(0, self.attack - damage)

        # double damage if the club suit power applies
        if club_check:
            damage *= 2

        self.health -= damage
        if self.health  == 0:
            return True

        self.health = max(0, self.health)
        return False