from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from src.theThing.players.schemas import PlayerForGame, PlayerBase
from src.theThing.cards.schemas import CardBase
from src.theThing.turn.schemas import TurnOut
from src.theThing.messages.schemas import MessageOut


class GameBase(BaseModel):
    # This is used to return a game before it started (it has no turn owner and play direction)
    name: str
    min_players: int
    max_players: int

    model_config = ConfigDict(from_attributes=True)


class GameCreate(GameBase):
    # This is used to create a game
    password: Optional[str] = None


class GameInDB(GameCreate):
    # This is used to return a game with the password and all the attributes saved
    id: int
    state: int = 0
    play_direction: Optional[bool] = None
    turn: Optional[TurnOut] = None
    players: List[PlayerBase] = None
    deck: List[CardBase] = None
    obstacles: Optional[List[int]] = []


class GameOut(BaseModel):
    # This is used to return a game without the password and the attributes saved in DB
    id: int
    name: str
    min_players: int
    max_players: int
    state: int = 0
    play_direction: Optional[bool] = None
    turn: Optional[TurnOut] = None
    players: List[PlayerForGame] = []
    obstacles: Optional[List[int]] = []

    model_config = ConfigDict(from_attributes=True)


class GamePlayerAmount(GameBase):
    # This is used to return a game with the amount of players
    # It is used in the list of games
    id: int
    amount_of_players: int

    model_config = ConfigDict(from_attributes=True)


class GameUpdate(BaseModel):
    # This is used to update a game
    state: Optional[int] = None
    play_direction: Optional[bool] = None
    obstacles: Optional[List[int]] = []
    model_config = ConfigDict(from_attributes=True)
