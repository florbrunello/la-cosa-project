from pony.orm import Required, Optional, PrimaryKey
from src.theThing.models.db import db


class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    code = Required(str)
    name = Required(str)
    kind = Required(
        int
    )  # 0 = action, 1 = defense, 2 = obstacle, 3 = infection(except "LaCosa"), 4 = panic, 5 = "LaCosa"
    description = Required(str)
    number_in_card = Required(int)
    state = Required(
        int, default=2, unsigned=True
    )  # 0 = played/discarded, 1 = in player hand, 2 = not played (in deck)
    playable = Required(bool)
    game = Required("Game", reverse="deck")
    player = Optional("Player", reverse="hand")

    def before_insert(self):
        self.state = 2
        # chek if kind is 0 1 2 3 4 5
        if self.kind not in [0, 1, 2, 3, 4, 5]:
            raise ValueError("The kind of the card is not valid")
