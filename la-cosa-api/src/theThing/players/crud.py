from pony.orm import ObjectNotFound
from pony.orm import db_session
from src.theThing.cards.schemas import CardBase

from src.theThing.games.models import Game
from src.theThing.players.schemas import PlayerCreate, PlayerUpdate, PlayerBase
from .models import Player
from ..cards.models import Card


def create_player(player_data: PlayerCreate, game_id: int):
    """
    It creates a player in the database from the
    PlayerCreate schema and returns the PlayerBase schema
    containing all the data from the player

    - If a player with the same name exists, then it cannot be created.
    - If the game does not exist, is full or started, then it cannot be created
    -> Then an exception its raised.
    """
    with db_session:
        try:
            game_to_join = Game[game_id]
        except ObjectNotFound:
            raise Exception("No se encontró la partida")
        if game_to_join.state != 0:
            raise Exception("La partida ya ha comenzado")
        elif game_to_join.max_players == len(game_to_join.players):
            raise Exception("La partida está llena")
        # check if a player with the same name exists in the list
        elif any(
            player.name == player_data.name for player in game_to_join.players
        ):
            raise Exception("Ya existe un jugador con el mismo nombre")

        player = Player(**player_data.model_dump(), game=game_to_join)
        player.table_position = len(game_to_join.players)
        # player_created contains the ponyorm object instance of the new player
        player.flush()  # flush the changes to the database
        response = PlayerBase.model_validate(player)
    return response


def get_player(player_id: int, game_id: int):
    """
    This function returns the PlayerBase schema from its id
    containing all the data from the player
    """
    with db_session:
        player = Player.get(game=Game[game_id], id=player_id)
        if player is None:
            raise ObjectNotFound(Player, pkval=player_id)

        if player.card_to_exchange is not None:
            card_to_exchange = CardBase.model_validate(
                Card[player.card_to_exchange]
            )
        else:
            card_to_exchange = None
        response = PlayerBase.model_validate(player, card_to_exchange)

    return response


def update_player(player: PlayerUpdate, player_id: int, game_id: int):
    """
    This function updates a player from the database
    and returns the PlayerBase schema with the updated data
    """
    with db_session:
        game = Game[game_id]
        player_to_update = Player.get(game=game, id=player_id)
        if player_to_update is None:
            raise ObjectNotFound(Player, pkval=player_id)

        if player.card_to_exchange is not None:
            player_to_update.set(
                **player.model_dump(
                    exclude_unset=True, exclude=["card_to_exchange"]
                )
            )
            player_to_update.card_to_exchange = player.card_to_exchange.id
        else:
            player_to_update.set(**player.model_dump(exclude_unset=True))
            player_to_update.card_to_exchange = None

        player_to_update.flush()
        if player_to_update.card_to_exchange is not None:
            card_to_exchange = CardBase.model_validate(
                Card[player_to_update.card_to_exchange]
            )
        else:
            card_to_exchange = None
        response = PlayerBase.model_validate(player_to_update, card_to_exchange)

    return response


def delete_player(player_id: int, game_id: int):
    """
    This function deletes a player from the database
    and returns a message with the result
    """
    with db_session:
        game = Game[game_id]
        player = Player.get(game=game, id=player_id)
        if player is None:
            raise ObjectNotFound(Player, pkval=player_id)
        player.delete()
    return {"message": f"Jugador {player_id} eliminado con éxito"}
