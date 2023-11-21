from src.theThing.models.db import db
from pony.orm import Required, Optional, PrimaryKey, composite_key, Set
from src.theThing.cards.models import Card


class Turn(db.Entity):
    """
    Represent a turn inside a game
    """

    game = PrimaryKey("Game", reverse="turn")
    owner = Optional(int)
    played_card = Optional(int)
    destination_player = Optional(str)
    response_card = Optional(int)
    destination_player_exchange = Optional(str)
    state = Optional(int)
    # 0 = stealing card, 1 = deciding (play/discard), 2 = waiting response,
    # 3 = exchanging cards, 4 = finished exchange, 5 = waiting to finish,
    # 6 = Panic card
