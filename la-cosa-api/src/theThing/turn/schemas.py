from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from src.theThing.cards.schemas import CardBase


class TurnCreate(BaseModel):
    # This is used to return a turn
    owner: Optional[int] = None  # player_id
    played_card: Optional[int] = None  # card_id
    destination_player: Optional[str] = None
    response_card: Optional[int] = None  # card_id
    destination_player_exchange: Optional[str] = None
    state: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TurnOut(TurnCreate):
    played_card: Optional[CardBase] = None
    response_card: Optional[CardBase] = None
