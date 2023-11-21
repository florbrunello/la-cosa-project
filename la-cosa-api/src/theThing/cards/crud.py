from .schemas import CardCreate, CardBase, CardUpdate
from .models import Card

# from ..games import models as gamemodel
from src.theThing.games.models import Game
from src.theThing.players.models import Player
from src.theThing.players.schemas import PlayerBase
from pony.orm import db_session, ObjectNotFound, select, flush


def create_card(card: CardCreate, game_id: int):
    """
    It creates a card in the database from the
    CardCreate schema and returns the CardBase schema
    containing all the data from the card.

    Also, it adds the card to the game deck.

    If the game does not exist, then it cannot be created.
    """
    with db_session:
        try:
            game = Game[game_id]
        except ObjectNotFound:
            raise Exception("No se encontró la partida")

        card = Card(
            code=card.code,
            name=card.name,
            kind=card.kind,
            description=card.description,
            number_in_card=card.number_in_card,
            playable=card.playable,
            game=game,
        )

        card.flush()
        response = CardBase.model_validate(card)
    return response


def get_card(card_id: int, game_id: int):
    """
    This function returns the CardBase schema from its id
    containing all the data from the card
    """
    with db_session:
        card = Card.get(game=Game[game_id], id=card_id)
        if card is None:
            raise ObjectNotFound(Card, pkval=card_id)
        response = CardBase.model_validate(card)
    return response


def delete_card(card_id: int, game_id: int):
    """
    This function deletes the card from the database
    """
    with db_session:
        card = Card.get(game=Game[game_id], id=card_id)
        if card is None:
            raise ObjectNotFound(Card, pkval=card_id)
        card.delete()
    return {
        "message": f"Carta {card_id} eliminada con éxito de la partida {game_id}"
    }


def give_card_to_player(card_id: int, player_id: int, game_id: int):
    """
    This function gives a card to a player
    """
    with db_session:
        card = Card.get(game=Game[game_id], id=card_id)
        if card is None:
            raise Exception("No se encontró la carta")
        player = Player.get(game=Game[game_id], id=player_id)
        if player is None:
            raise Exception("No se encontró el jugador")
        card.player = player
        card.state = 1
        card.flush()
        response = CardBase.model_validate(card)
    return response


def get_card_from_deck(game_id: int):
    """
    This function returns a card from the deck
    """
    with db_session:
        game = Game[game_id]
        if len(game.deck) == 0:
            raise Exception("La carta no existe en el mazo")

        # Select a card from the deck
        card = game.deck.select(lambda c: c.state == 2).random(1)
        if card == []:
            # If there is no cards left in the game deck, shuffle the deck
            card_state_0 = game.deck.select(lambda c: c.state == 0)
            for card in card_state_0:
                card.state = 2
            flush()

        card = game.deck.select(lambda c: c.state == 2).random(1)[0]

        response = CardBase.model_validate(card)
        return response


def update_card(card_to_update: CardUpdate, game_id: int):
    """
    This function updates the card state
    """
    with db_session:
        card = Card.get(game=Game[game_id], id=card_to_update.id)
        if card is None:
            raise ObjectNotFound(Card, pkval=card_to_update.id)
        card.state = card_to_update.state
        card.flush()
        response = CardBase.model_validate(card)
    return response


def remove_card_from_player(card_id: int, player_id: int, game_id: int):
    """
    This function removes a card from a player and returns the player
    """
    with db_session:
        card = Card.get(game=Game[game_id], id=card_id)
        if card is None:
            raise ObjectNotFound(Card, pkval=card_id)
        player = Player.get(game=Game[game_id], id=player_id)
        if player is None:
            raise ObjectNotFound(Player, pkval=player_id)
        card.player = None
        card.state = 0
        flush()
        # look for the player again to have his hand updated
        player = Player.get(game=Game[game_id], id=player_id)
        response = PlayerBase.model_validate(player)
    return response
