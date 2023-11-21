from . import schemas, models
from pony.orm import db_session
from .schemas import TurnCreate


def create_turn(game_id: int, turn_owner: int, exchange_player: str):
    with db_session:
        turn = models.Turn(
            game=game_id,
            owner=turn_owner,
            destination_player_exchange=exchange_player,
            state=0,
        )
        turn.flush()
        response = schemas.TurnCreate.model_validate(turn)
    return response


def update_turn(game_id: int, new_turn: TurnCreate):
    """
    This functions updates a game with game_id
    with the data in the GameUpdate schema
    """
    with db_session:
        turn_to_update = models.Turn[game_id]
        turn_to_update.set(**new_turn.model_dump(exclude_unset=True))
        turn_to_update.flush()
        response = schemas.TurnCreate.model_validate(turn_to_update)
    return response
