import socketio
from src.theThing.cards.schemas import CardBase
from src.theThing.players.schemas import PlayerBase
from src.theThing.games.schemas import GameOut, GameInDB
from src.theThing.players.crud import get_player
from urllib.parse import parse_qs
from src.theThing.games.crud import get_game
from src.theThing.messages.schemas import MessageOut
from src.theThing.cards.special_effect_applications import apply_cac, apply_olv

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
# define an asgi app
socketio_app = socketio.ASGIApp(sio, socketio_path="/")


@sio.event
async def connect(sid, environ):
    print("connect ", sid)
    query_string = environ.get("QUERY_STRING", "")
    params = parse_qs(query_string)
    player_id = params.get("Player-Id", [None])[0]
    game_id = params.get("Game-Id", [None])[0]
    # if the parameters are not present, the connection is rejected
    if not player_id or not game_id:
        return False
    await sio.save_session(sid, {"player_id": player_id, "game_id": game_id})
    await sio.enter_room(sid, "g" + game_id)
    await sio.enter_room(sid, "p" + player_id)
    print("connect ", sid, "player_id ", player_id, "game_id ", game_id)
    # This is necessary for the client connection logic
    game_to_send = get_game(game_id)
    player_to_send = get_player(player_id, game_id)
    await send_game_status_to_players(game_id, game_to_send)
    await send_player_status_to_player(player_id, player_to_send)


@sio.event
async def disconnect(sid):
    print("disconnect ", sid)


async def send_player_status_to_player(player_id: int, player_data: PlayerBase):
    await sio.emit(
        "player_status", player_data.model_dump(), room="p" + str(player_id)
    )


async def send_game_status_to_players(game_id: int, game_data: GameOut):
    """
    Sends the game status to ALL players in the game
    :param game_id:
    :param game_data:
    :return:
    """
    await sio.emit(
        "game_status", game_data.model_dump(), room="g" + str(game_id)
    )


async def send_game_and_player_status_to_players(game_data: GameInDB):
    for player in game_data.players:
        await sio.emit(
            "player_status", player.model_dump(), room="p" + str(player.id)
        )
    game_to_send = GameOut.model_validate_json(game_data.model_dump_json())
    await sio.emit(
        "game_status", game_to_send.model_dump(), room="g" + str(game_data.id)
    )


async def send_new_message_to_players(game_id: int, message: MessageOut):
    await sio.emit("new_message", message.model_dump(), room="g" + str(game_id))


async def send_finished_game_event_to_players(game_id: int, data: dict):
    winners = data.get("winners")
    message = data.get("reason")
    await sio.emit(
        "game_finished",
        {"winners": winners, "log": message},
        room="g" + str(game_id),
    )


async def send_action_event_to_players(game_id: int, message: str):
    await sio.emit(
        "action",
        data={
            "log": message,
        },
        room="g" + str(game_id),
    )


async def send_discard_event_to_players(
    game_id: int, player_name: str, message: str
):
    await sio.emit(
        "discard",
        {
            "player_name": player_name,
            "log": message,
        },
        room="g" + str(game_id),
    )


async def send_defense_event_to_players(
    game_id: int,
    message: str,
):
    await sio.emit(
        "defense",
        data={"log": message},
        room="g" + str(game_id),
    )


async def send_exchange_event_to_players(
    game_id: int, exchanging_offerer: str, defending_player: str
):
    await sio.emit(
        "exchange",
        data={
            "log": exchanging_offerer
            + " intercambió cartas con "
            + defending_player
        },
        room="g" + str(game_id),
    )


async def send_finished_turn_to_players(
    game_id: int, message: str, new_owner_name: str, new_owner_position: int
):
    await sio.emit(
        "turn_finished",
        data={
            "log": message,
            "new_owner_name": new_owner_name,
            "new_owner_position": new_owner_position,
        },
        room="g" + str(game_id),
    )


async def send_quarantine_event_to_players(
    game_id: int, card: CardBase, message: str
):
    card_to_send = card.model_dump(exclude={"id"})
    await sio.emit(
        "quarantine",
        data={"log": message, "cards": [card_to_send]},
        room="g" + str(game_id),
    )


async def send_panic_event_to_players(
    game_id: int, card: CardBase, message: str
):
    card_to_send = card.model_dump(exclude={"id"})
    await sio.emit(
        "panic",
        data={"log": message, "cards": [card_to_send]},
        room="g" + str(game_id),
    )


async def send_analysis_to_player(
    player_id: int, hand: [CardBase], attacked_player_name: str
):
    # include all data from the cards except the id
    data_to_send = [card.model_dump(exclude={"id"}) for card in hand]
    await sio.emit(
        "analisis",
        data={
            "log": "Estas son las cartas de" + attacked_player_name,
            "cards": data_to_send,
        },
        room="p" + str(player_id),
    )


async def send_suspicion_to_player(
    player_id: int, card: CardBase, attacked_player_name: str
):
    data_to_send = card.model_dump(exclude={"id"})
    await sio.emit(
        "sospecha",
        data={
            "log": "Esta es una carta de" + attacked_player_name,
            "cards": [data_to_send],
        },
        room="p" + str(player_id),
    )


async def send_whk_to_player(game_id: int, player: str, hand: [CardBase]):
    data_to_send = [card.model_dump(exclude={"id"}) for card in hand]
    await sio.emit(
        "whisky",
        data={
            "log": player + "jugó whisky y estas son sus cartas!",
            "cards": data_to_send,
        },
        room="g" + str(game_id),
    )


async def send_ate_to_player(
    game_id: int, player: PlayerBase, dest_player: PlayerBase, card: CardBase
):
    data_to_send = [card.model_dump(exclude={"id"})]
    await sio.emit(
        "ate",
        data={
            "log": f"Esta es la carta que {player.name} quiso intercambiar",
            "cards": data_to_send,
        },
        room="p" + str(dest_player.id),
    )


async def send_ups_to_players(game_id: int, player: str, hand: [CardBase]):
    data_to_send = [card.model_dump(exclude={"id"}) for card in hand]
    await sio.emit(
        "ups",
        data={
            "log": player + "jugó ¡Ups! y estas son sus cartas!",
            "cards": data_to_send,
        },
        room="g" + str(game_id),
    )


async def send_qen_to_player(
    game_id: int, hand: [CardBase], dest_player: PlayerBase
):
    data_to_send = [card.model_dump(exclude={"id"}) for card in hand]
    await sio.emit(
        "qen",
        data={
            "log": dest_player.name
            + "jugó Que quede entre nosotros y estas son sus cartas!",
            "cards": data_to_send,
        },
        room="p" + str(dest_player.id),
    )


async def send_cpo_to_players(game_id: int):
    await sio.emit(
        "cpo",
        data={
            "log": "¡Las viejas cuerdas que usaste son fáciles de romper! Todas las cartas "
            "Todas las cartas 'Cuarentena' que haya en juego son descartadas",
        },
        room="g" + str(game_id),
    )


@sio.on("cac")
async def receive_cac_event(sid, data):
    player, game = await apply_cac(data)

    await send_game_status_to_players(game.id, game)
    await send_player_status_to_player(player.id, player)


@sio.on("olv")
async def receive_olv_event(sid, data):
    player, game = await apply_olv(data)

    await send_game_status_to_players(game.id, game)
    await send_player_status_to_player(player.id, player)
