from enum import Flag
from fastapi import HTTPException
from httpx import get
from pony.orm import ObjectNotFound as ExceptionObjectNotFound
from .crud import get_full_game, update_game, get_game
from .schemas import GameOut, GameInDB, GameUpdate
from ..cards.crud import get_card, give_card_to_player, remove_card_from_player
from ..turn.crud import update_turn
from ..turn.schemas import TurnCreate
import random
from ..players.crud import get_player, update_player
from ..players.schemas import PlayerBase, PlayerUpdate


# Function to verify configuration data integrity
def verify_data_create(game_name, min_players, max_players, host_name):
    """
    Verify the integrity of game configuration data.

    Parameters:
    - game_name (str): The name of the game.
    - min_players (int): The minimum number of players.
    - max_players (int): The maximum number of players.
    - host_name (str): The name of the host.

    Raises:
    - HTTPException (status_code=422): If game or host name is empty, or if min_players is less than 4 or max_players
    is greater than 12.

    Returns:
    - None
    """
    if not game_name:
        raise HTTPException(
            status_code=422, detail="El nombre de la partida no puede ser vacío"
        )

    if not host_name:
        raise HTTPException(
            status_code=422, detail="El nombre del host no puede ser vacío"
        )

    if min_players < 4:
        raise HTTPException(
            status_code=422,
            detail="El mínimo de jugadores no puede ser menor a 4",
        )

    if max_players > 12:
        raise HTTPException(
            status_code=422,
            detail="El máximo de jugadores no puede ser mayor a 12",
        )

    if min_players > max_players:
        raise HTTPException(
            status_code=422,
            detail="El mínimo de jugadores no puede ser mayor al máximo",
        )


# Function to verify configuration data integrity
def verify_data_start(game: GameOut, host_name: str):
    """
    Verify the integrity of game configuration data.

    Parameters:
    - game_id (int): The ID of the game to join.
    - player_name (str): The name of the player.

    Raises:
    - HTTPException (status_code=422): If game or host name is empty, or if min_players is less than 4 or max_players
    is greater than 12.

    Returns:
    - None
    """
    if len(game.players) < game.min_players:
        raise HTTPException(
            status_code=422,
            detail="No hay suficientes jugadores para iniciar la partida",
        )

    if len(game.players) > game.max_players:
        raise HTTPException(
            status_code=422,
            detail="Hay demasiados jugadores para iniciar la partida",
        )

    if host_name not in [player.name for player in game.players]:
        raise HTTPException(
            status_code=422, detail="El host no está dentro de la partida"
        )

    for player in game.players:
        if player.name == host_name:
            if not player.owner:
                raise HTTPException(
                    status_code=422,
                    detail="El jugador provisto no es el host de la partida",
                )
            else:
                break

    if game.state != 0:
        raise HTTPException(
            status_code=422, detail="La partida especificada ya comenzó"
        )


def verify_finished_game(game: GameOut):
    game = get_full_game(game.id)
    winners = None
    reason = None
    turn_owner_name = [
        player.name
        for player in game.players
        if player.table_position == game.turn.owner
    ][0]
    the_thing = [player for player in game.players if player.role == 3][0]
    if game.turn.played_card is not None:
        if (
            game.turn.played_card.code == "lla"
            and game.turn.response_card is None
            and game.turn.destination_player == the_thing.name
        ):
            # if a flamethrower was played and killed "La cosa", the game ends and all alive humans win
            game.state = 2
            game_id = game.id
            game_new_state = GameUpdate(state=game.state)
            game = update_game(game_id, game_new_state)
            winners = [
                player.name
                for player in game.players
                if (player.role == 1 and player.alive)
            ]
            reason = (
                "La cosa fue eliminada por "
                + turn_owner_name
                + " ganaron todos los humanos vivos"
            )

    amount_infected_players = len(
        [
            player
            for player in game.players
            if (player.role == 2 and player.alive)
        ]
    )
    if amount_infected_players == len(game.players) - 1:
        # if "La cosa" infected all players, the game ends and "La cosa" wins
        game.state = 2
        game_id = game.id
        game_new_state = GameUpdate(state=game.state)
        game = update_game(game_id, game_new_state)
        winners = [
            player.name
            for player in game.players
            if (player.role == 3 and player.alive)
        ]
        reason = "La cosa infectó a todos los jugadores y gano la partida"

    # if it only remains one player alive its the winner, if "La cosa" is the last one, then infected also wins
    alive_players = [player for player in game.players if player.alive]
    if len(alive_players) == 1:
        game.state = 2
        game_id = game.id
        game_new_state = GameUpdate(state=game.state)
        game = update_game(game_id, game_new_state)
        winners = [player.name for player in alive_players]
        if alive_players[0].role == 3:
            reason = "La cosa fue el último jugador vivo y ganó la partida"
        else:
            reason = (
                alive_players[0].name
                + " fue el último jugador vivo y ganó la partida"
            )
    return_data = {"game": game, "winners": winners, "reason": reason}
    return return_data


def verify_data_play_card(
    game_id: int, player_id: int, card_id: int, destination_name: str
):
    # Verify that the game exists and it is started
    try:
        game = get_full_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404, detail=str("No se encontró la partida")
        )
    if game.state != 1:
        raise HTTPException(
            status_code=422, detail="La partida aún no ha comenzado"
        )

    # Verify that the player exists, and it is the turn owner and it is alive
    try:
        player = get_player(player_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=422,
            detail=str("No se encontró el jugador especificado"),
        )
    if game.turn.owner != player.table_position or not player.alive:
        raise HTTPException(
            status_code=422, detail="No es el turno del jugador especificado"
        )
    if game.turn.state != 1:
        raise HTTPException(
            status_code=422,
            detail="El jugador todavia no puede jugar en este turno",
        )
    # Verify that the card exists and it is in the player hand
    try:
        card = get_card(card_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=422, detail=str("No se encontró la carta especificada")
        )
    if card not in player.hand or card not in game.deck or card.state == 0:
        raise HTTPException(
            status_code=422,
            detail="La carta no pertenece a la mano del jugador o al mazo de la partida",
        )
    if card.kind not in [0, 2, 4]:
        raise HTTPException(
            status_code=422, detail="No puedes jugar esta carta"
        )
    if card.playable is False:
        raise HTTPException(
            status_code=422, detail="La carta seleccionada no es jugable"
        )
    if len(player.hand) <= 4:
        raise HTTPException(
            status_code=422,
            detail="El jugador tiene menos cartas de las necesarias para jugar",
        )
    # Get the destination player by his name and check that is not the same player and exists and is alive
    destination_player = None
    for p in game.players:
        if p.name == destination_name:
            destination_player = p
            break
    if destination_player is None:
        raise HTTPException(
            status_code=422, detail="No se encontró al jugador objetivo"
        )
    if destination_player.id == player.id and card.code not in [
        "whk",
        "vte",
        "cpo",
        "trc",
        "eaf",
        "hac",
        "ups",
        "cac",
        "olv",
    ]:
        raise HTTPException(
            status_code=422,
            detail="No se puede aplicar el efecto a sí mismo",
        )
    if not destination_player.alive:
        raise HTTPException(
            status_code=422, detail="El jugador objetivo no está vivo"
        )
    alive_players = [p.table_position for p in game.players if p.alive]
    alive_players.sort()
    index_player = alive_players.index(player.table_position)
    index_destination_player = alive_players.index(
        destination_player.table_position
    )
    if card.code not in [
        "mvc",
        "whk",
        "vte",
        "sed",
        "cpo",
        "und",
        "sda",
        "trc",
        "eaf",
        "hac",
        "ups",
        "npa",
        "cac",
        "olv",
    ]:
        # check if the destination !=player is adjacent to the player,
        # the first and the last player are adjacent
        if index_destination_player == (index_player + 1) % len(
            alive_players
        ) or index_destination_player == (index_player - 1) % len(
            alive_players
        ):
            pass
        else:
            raise HTTPException(
                status_code=422,
                detail="El jugador destino no está sentado en una posición adyacente",
            )
    # Check for obstacles
    if (
        len(game.obstacles) > 0
        and destination_name != player.name
        and (
            card.code
            not in [
                "whk",
                "vte",
                "sed",
                "mvc",
                "hac",
                "und",
                "trc",
                "eaf",
                "vyv",
                "npa",
                "cac",
                "olv",
            ]
        )
    ):
        door_flag = False
        player_position = player.table_position
        destination_player_position = destination_player.table_position
        if (  # played to the left case 1
            player_position == alive_players[0]
            and destination_player_position == alive_players[-1]
        ):
            if destination_player_position in game.obstacles:
                door_flag = True
        elif (  # played to the right case 1
            player_position == alive_players[-1]
            and destination_player_position == alive_players[0]
        ):
            if player_position in game.obstacles:
                door_flag = True
        elif (  # played to the left case 2
            player_position > destination_player_position
        ):
            if destination_player_position in game.obstacles:
                door_flag = True
        elif (  # played to the right case 2
            player_position < destination_player_position
        ):
            if player_position in game.obstacles:
                door_flag = True
        if door_flag:
            raise HTTPException(
                status_code=422,
                detail="No es posible jugar esta carta al jugador, existe una puerta atrancada entre ambos",
            )
    return game, player, card, destination_player


def verify_data_steal_card(game_id: int, player_id: int):
    # Verify that the game exists and it is started
    try:
        game = get_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404, detail=str("No se encontró la partida")
        )
    if game.state != 1:
        raise HTTPException(
            status_code=422, detail="La partida aún no ha comenzado"
        )
    if game.turn.state != 0:
        raise HTTPException(
            status_code=422,
            detail="No es posible robar una carta en este momento",
        )

    # Check valid player status
    try:
        player = get_player(player_id, game_id)
        if len(player.hand) >= 5:
            raise HTTPException(
                status_code=422, detail="La mano del jugador está llena"
            )
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=422, detail=str("No se encontró el jugador")
        )

    # Verify that it actually is the player turn
    if game.turn.owner != player.table_position:
        raise HTTPException(status_code=422, detail="No es tu turno")


def verify_data_generic(game_id: int, player_id: int, card_id: int):
    # Verify that the game exists and it is started
    try:
        game = get_full_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail="No se encontró la partida")
    if game.state != 1:
        raise HTTPException(
            status_code=422, detail="La partida aún no ha comenzado"
        )

    # Verify that the player exists, and it is the turn owner and is alive.
    try:
        player = get_player(player_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404, detail="No se encontró el jugador especificado"
        )
    if game.turn.owner != player.table_position or not player.alive:
        raise HTTPException(
            status_code=422, detail="No es el turno del jugador especificado"
        )

    # Verify that the card exists and it is in the player hand
    try:
        card = get_card(card_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404, detail="No se encontró la carta especificada"
        )
    if card.kind == 5:
        raise HTTPException(
            status_code=422, detail="No es posible descartar esta carta"
        )
    if card not in player.hand or card not in game.deck or card.state == 0:
        raise HTTPException(
            status_code=422,
            detail="La carta no pertenece a la mano del jugador o al mazo de la partida",
        )
    if card.playable is False:
        raise HTTPException(
            status_code=422, detail="La carta seleccionada no es jugable"
        )

    return game, player, card


def verify_data_discard_card(game_id: int, player_id: int, card_id: int):
    try:
        game, player, card = verify_data_generic(game_id, player_id, card_id)
    except HTTPException as e:
        raise e

    if game.turn.state != 1:
        raise HTTPException(
            status_code=422, detail="No es posible descartar en este momento"
        )

    if len(player.hand) <= 4:
        raise HTTPException(
            status_code=422,
            detail="No es posible descartar sin robar una carta primero",
        )

    infected_cards = [card for card in player.hand if card.code == "inf"]
    if (
        len(infected_cards) == 1
        and infected_cards[0].id == card.id
        and player.role == 2
    ):
        raise HTTPException(
            status_code=422,
            detail="No es posible descartar la última carta de infección",
        )

    return game, player, card


def verify_data_response_basic(game_id: int, defending_player_id: int):
    # It also returns the game, the attacking player, the defending player and the action card
    # Game checks
    try:
        game = get_full_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail="No se encontró la partida")
    if game.state != 1:
        raise HTTPException(
            status_code=422, detail="La partida aún no ha comenzado"
        )
    if game.turn.state != 2:
        raise HTTPException(
            status_code=422, detail="No es posible defenderse en este momento"
        )

    # Check if the attacking player exists and its alive
    for player in game.players:
        if player.table_position == game.turn.owner:
            attacking_player = player
            break
    if attacking_player is None:
        raise HTTPException(
            status_code=404, detail="No se encontró el jugador atacante"
        )
    if not attacking_player.alive:
        raise HTTPException(
            status_code=422, detail="El jugador atacante está muerto"
        )
    # Check the defending player exists and its alive
    try:
        defending_player = get_player(defending_player_id, game_id)
    except Exception as e:
        raise HTTPException(
            status_code=404, detail="No se encontró el jugador destino"
        )

    # Check the action card state
    try:
        action_card = get_card(game.turn.played_card.id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la carta de ataque especificada",
        )
    if action_card.state != 0:
        raise HTTPException(
            status_code=422, detail="La carta de ataque no ha sido jugada"
        )
    attacking_player = get_player(attacking_player.id, game_id)
    return game, attacking_player, defending_player, action_card


def verify_data_exchange(game_id: int, player_id: int, card_id: int):
    try:
        game, player, card = verify_data_generic(game_id, player_id, card_id)
    except HTTPException as e:
        raise e

    if game.turn.state != 3:
        raise HTTPException(
            status_code=422, detail="No es posible intercambiar en este momento"
        )
    # Get the destination_player
    for p in game.players:
        if p.name == game.turn.destination_player_exchange:
            destination_player = p
            break
    # If the card is inf, check that the player is "La Cosa" or is an infected player offering the card to "La Cosa"
    if card.code == "inf":
        if player.role == 1:
            raise HTTPException(
                status_code=422,
                detail="No es posible intercambiar esta carta",
            )
        else:
            if player.role == 2 and destination_player.role != 3:
                raise HTTPException(
                    status_code=422,
                    detail="No es posible intercambiar esta carta con este jugador",
                )

    # If the card is "lco" raises an exception
    if card.code == "lco":
        raise HTTPException(
            status_code=422, detail="No es posible intercambiar esta carta"
        )

    infected_cards = [card for card in player.hand if card.code == "inf"]
    if (
        len(infected_cards) == 1
        and card.id == infected_cards[0].id
        and player.role == 2
    ):
        raise HTTPException(
            status_code=422,
            detail="No es posible intercambiar la última carta de infección",
        )
    if len(game.obstacles) > 0:
        if (
            player.table_position in game.obstacles and game.play_direction
        ) or (
            destination_player.table_position in game.obstacles
            and not game.play_direction
        ):
            raise Exception("Existe una puerta atrancada")

    return game, player, card


def verify_data_exchange_basic(game_id: int, defending_player_id: int):
    # It also returns the game, the attacking player, the defending player and the action card
    # Game checks
    try:
        game = get_full_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail="No se encontró la partida")
    if game.state != 1:
        raise HTTPException(
            status_code=422, detail="La partida aún no ha comenzado"
        )
    if game.turn.state != 4:
        raise HTTPException(
            status_code=422,
            detail="No es posible defenderse de un intercambio en este momento",
        )

    # Check if the exchanging offerer exists and its alive
    for player in game.players:
        if player.table_position == game.turn.owner:
            exchanging_offerer = player
            break

    if exchanging_offerer is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el jugador que ofertó el intercambio",
        )
    if not exchanging_offerer.alive:
        raise HTTPException(
            status_code=422,
            detail="El jugador que ofreció el intercambio está muerto",
        )
    # Check the defending player exists and its alive
    try:
        defending_player = get_player(defending_player_id, game_id)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el jugador destino del intercambio",
        )

    if defending_player.name != game.turn.destination_player_exchange:
        raise HTTPException(
            status_code=422,
            detail="El jugador destino del intercambio no es el correcto",
        )

    return game, exchanging_offerer, defending_player


def exchange_cards_effect(
    game_id: int,
    exchanging_offerer: PlayerBase,
    defending_player: PlayerBase,
    exchange_card_id: int,
):
    # swap cards in the player's hand from the defending player and the offerer
    # Get the card to exchange from the defending player
    try:
        exchange_card = get_card(exchange_card_id, game_id)
        offered_card = get_card(exchanging_offerer.card_to_exchange.id, game_id)
    except Exception as e:
        raise e
    if (
        exchange_card not in defending_player.hand
        or offered_card not in exchanging_offerer.hand
    ):
        raise HTTPException(
            status_code=404,
            detail="Las cartas de los intercambios no están en la mano de los jugadores",
        )
    # If the card is inf, check that the player is "La Cosa" or is an infected player offering the card to "La Cosa"
    if exchange_card.code == "inf":
        if defending_player.role == 1:
            raise HTTPException(
                status_code=422,
                detail="No es posible intercambiar esta carta",
            )
        else:
            if defending_player.role == 2 and exchanging_offerer.role != 3:
                raise HTTPException(
                    status_code=422,
                    detail="No es posible intercambiar esta carta con este jugador",
                )

    infected_cards = [
        card for card in defending_player.hand if card.code == "inf"
    ]
    if (
        len(infected_cards) == 1
        and exchange_card.id == infected_cards[0].id
        and defending_player.role == 2
    ):
        raise HTTPException(
            status_code=422,
            detail="No es posible intercambiar la última carta de infección",
        )
    # If the card is "lco" raises an exception
    if exchange_card.code == "lco":
        raise HTTPException(
            status_code=422, detail="No es posible intercambiar esta carta"
        )

    # Swap the cards
    defending_player = remove_card_from_player(
        exchange_card.id, defending_player.id, game_id
    )
    exchanging_offerer = remove_card_from_player(
        offered_card.id, exchanging_offerer.id, game_id
    )
    game = get_game(game_id)
    # If offered_card.code is "inf" and exchanging_offerer.role="laCosa", change the defending player role to infected.
    
    if (
        offered_card.code == "inf"
        and exchanging_offerer.role == 3
    ):
        if game.turn.played_card is not None:
            if game.turn.played_card.code != "fal":
                update_player(PlayerUpdate(role=2), defending_player.id, game_id)
        else: 
            update_player(PlayerUpdate(role=2), defending_player.id, game_id)
    # If the defending player is La Cosa and gives an infected card
    elif (
        exchange_card.code == "inf"
        and defending_player.role == 3
    ):
        if game.turn.played_card.code is not None:
            if game.turn.played_card.code != "fal":
                update_player(PlayerUpdate(role=2), exchanging_offerer.id, game_id)
        else:
            update_player(PlayerUpdate(role=2), exchanging_offerer.id, game_id)
    # Clean the field card_to_exchange from the offerer player
    exchanging_offerer = update_player(
        PlayerUpdate(card_to_exchange=None), exchanging_offerer.id, game_id
    )
    # Give the cards to the players
    give_card_to_player(exchange_card.id, exchanging_offerer.id, game_id)
    give_card_to_player(offered_card.id, defending_player.id, game_id)


def verify_data_response_card(
    game_id: int, defending_player: PlayerBase, response_card_id: int
):
    # It also returns the response card
    # Get defense card
    try:
        response_card = get_card(response_card_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la carta de defensa especificada",
        )
    if response_card.kind != 1:
        raise HTTPException(
            status_code=422, detail="No te puedes defender con esta carta"
        )
    # Player checks
    if len(defending_player.hand) != 4:
        raise HTTPException(
            status_code=422,
            detail="El jugador tiene menos o más de 4 cartas en su mano. Debería tener 4.",
        )
    if response_card not in defending_player.hand:
        raise HTTPException(
            status_code=404,
            detail="La carta de defensa no está en la mano del jugador",
        )
    return response_card


def assign_hands(game: GameInDB):
    """
    Assign the initial hands to the players following the process specified by game rules.

    Parameters:
    - game (GameInDB): The full game data.

    Returns:
    - None
    """
    amount_of_players = len(game.players)
    full_deck = game.deck
    # Remove infection, panic and The Thing cards from the deck
    remaining_cards = [
        card
        for card in full_deck
        if card.kind != 3 and card.kind != 4 and card.kind != 5
    ]
    the_thing_card = [card for card in full_deck if card.kind == 5][0]

    # set aside 4 cards per player - 1
    set_aside_amount = 4 * amount_of_players - 1
    set_aside_cards = remaining_cards[:set_aside_amount]
    set_aside_cards.append(the_thing_card)
    random.shuffle(set_aside_cards)

    # assign the cards to the players
    for player in game.players:
        player_cards = set_aside_cards[:4]
        set_aside_cards = set_aside_cards[4:]

        # assign corresponding role
        if len([card for card in player_cards if card.kind == 5]) > 0:
            update_player(PlayerUpdate(role=3), player.id, game.id)
        else:
            update_player(PlayerUpdate(role=1), player.id, game.id)

        for card in player_cards:
            give_card_to_player(card.id, player.id, game.id)


def verify_data_finish_turn(game_id: int):
    """
    Verify the integrity of finish turn data.
    """

    # Verify that the game exists and it is started
    try:
        game = get_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404, detail=str("No se encontró la partida")
        )

    if game.state != 1:
        raise HTTPException(
            status_code=422, detail="La partida aún no ha comenzado"
        )

    if game.turn.state != 5:
        raise HTTPException(
            status_code=422, detail="El turno aún no ha terminado"
        )

    return game


def assign_turn_owner(game: GameOut):
    played_card = game.turn.played_card
    if played_card is not None:
        # If played_card is None, then it was discarded, and we need to skip this section
        played_card_code = played_card.code
        response_card = game.turn.response_card
        cards_change_places = ["cdl", "mvc", "und", "sda"]
        if (played_card_code in cards_change_places) and response_card is None:
            # If the played card is "cdl" or "mvc" and there's no response, the turn
            # owner is the position of the destination player
            for player in game.players:
                if player.name == game.turn.destination_player:
                    new_owner = player.table_position
                    break
            new_dest_exch = get_player_in_next_n_places(game, new_owner, 1)
            update_turn(
                game.id,
                TurnCreate(
                    owner=new_owner,
                    state=0,
                    played_card=None,
                    response_card=None,
                    destination_player="",
                    destination_player_exchange=new_dest_exch.name,
                ),
            )

            return

    # Assign new turn owner, must be an alive player
    # if play direction is clockwise, turn owner is the next player.
    # If not, the previous player
    game = get_game(game.id)
    new_turn_owner = get_player_in_next_n_places(game, game.turn.owner, 1)
    new_exchange_player = get_player_in_next_n_places(game, game.turn.owner, 2)
    update_turn(
        game.id,
        TurnCreate(
            owner=new_turn_owner.table_position,
            state=0,
            played_card=None,
            response_card=None,
            destination_player="",
            destination_player_exchange=new_exchange_player.name,
        ),
    )


def get_player_in_next_n_places(game: GameOut, owner: int, n: int):
    """
    Get the player that is n places after the player in the table.
    According to the play direction

    Parameters:
    - game (GameOut): The game data.
    - player (PlayerBase): The player to start counting from.
    - n (int): The number of places to count.

    Returns:
    - PlayerBase: The player that is n places after the player in the table.
    """
    alive_players = [
        player.table_position for player in game.players if player.alive
    ]
    alive_players.sort()
    index_player = alive_players.index(owner)
    if game.play_direction:
        next_player = alive_players[(index_player + n) % len(alive_players)]
    else:
        next_player = alive_players[(index_player - n) + len(alive_players) % len(alive_players)]
    for p in game.players:
        if p.table_position == next_player:
            return p


def calculate_winners_if_victory_declared(game_id, player_id):
    try:
        game = get_full_game(game_id)
        player = get_player(player_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    if game.state != 1:
        raise HTTPException(
            status_code=422, detail="La partida no está en juego"
        )

    if player.role != 3:
        raise HTTPException(status_code=422, detail="El jugador no es La Cosa")

    win = True
    alive_humans = []
    alive_infected = []

    for player in game.players:
        if player.alive:
            if player.role == 1:
                win = False
                alive_humans.append(player.name)
            elif player.role != 1:
                alive_infected.append(player.name)

    if win:
        result = {
            "reason": "¡No quedan humano vivos! Gana La Cosa e infectados",
            "winners": alive_infected,
        }
    else:
        result = {
            "reason": "¡La cosa se equivocó! Ganan los humanos",
            "winners": alive_humans,
        }

    return result


def update_quarantine_status(game):
    """ """
    turn_owner_position = game.turn.owner

    for player in game.players:
        if player.table_position == turn_owner_position:
            player_to_update = player

    if player_to_update.quarantine > 0:
        player = get_player(player_to_update.id, game.id)
        new_quarantine = player.quarantine - 1
        update_player(
            PlayerUpdate(quarantine=new_quarantine),
            player_to_update.id,
            game.id,
        )


def verify_obstacles_for_exchange(
    game: GameOut, player: PlayerBase, destination_player: PlayerBase
):
    if len(game.obstacles) > 0:
        if (
            player.table_position in game.obstacles and game.play_direction
        ) or (
            destination_player.table_position in game.obstacles
            and not game.play_direction
        ):
            raise Exception("Existe una puerta atrancada")
