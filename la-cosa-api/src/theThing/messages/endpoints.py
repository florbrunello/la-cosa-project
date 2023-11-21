from fastapi import APIRouter, HTTPException
from src.theThing.games.crud import get_game
from src.theThing.messages.crud import create_message, get_chat
from src.theThing.messages.schemas import MessageCreate
from src.theThing.games.socket_handler import send_new_message_to_players
from pony.orm import ObjectNotFound as ExceptionObjectNotFound

message_router = APIRouter()


@message_router.put("/game/{game_id}/send-message")
async def send_message(game_id: int, message: MessageCreate):
    """
    Send a message to the game chat.
    :param game_id:
    :param message:
    :return: 200 OK if message created successfully

    :raises: 404 if game not found
    """
    try:
        game = get_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        message = create_message(message, game_id)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    await send_new_message_to_players(game_id, message)
    return {
        "message": "Mensaje enviado con exito",
        "data": message.model_dump(),
    }


@message_router.get("/game/{game_id}/chat")
async def get_chat_messages(game_id: int):
    """
    Get the messages from the game chat.
    :param game_id:
    :return: list of messages

    :raises: 404 if game not found
    """
    try:
        game = get_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        chat = get_chat(game_id)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    return chat
