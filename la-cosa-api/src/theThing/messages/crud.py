from src.theThing.messages.schemas import MessageCreate, MessageOut
from src.theThing.messages.models import Message
from src.theThing.games.models import Game
from datetime import datetime
from pony.orm import db_session, ObjectNotFound, select, flush


@db_session
def create_message(message: MessageCreate, game_id: int) -> MessageOut:
    """
    This function creates a message in the database
    from the MessageCreate schema and returns the
    MessageOut schema containing all the data from the message.

    If the game does not exist, then it cannot be created.
    """
    try:
        game = Game[game_id]
    except ObjectNotFound:
        raise Exception("No se encontró la partida")

    message = Message(
        sender=message.sender,
        content=message.content,
        date=datetime.now(),
        game=game,
    )

    message.flush()
    response = MessageOut.model_validate(message)
    return response


@db_session
def get_chat(game_id: int) -> list[MessageOut]:
    """
    This function returns the messages from the game
    """
    try:
        game = Game[game_id]
    except ObjectNotFound:
        raise Exception("No se encontró la partida")

    messages = select(m for m in Message if m.game == game).order_by(
        Message.date
    )[:]
    response = [MessageOut.model_validate(message) for message in messages]
    return response
