from pony.orm import PrimaryKey, Optional, Required
from datetime import datetime
from src.theThing.models.db import db


class Message(db.Entity):
    id = PrimaryKey(int, auto=True)
    sender = Optional(str)
    content = Optional(str, 128)
    date = Optional(datetime)
    game = Required("Game", reverse="chat")
