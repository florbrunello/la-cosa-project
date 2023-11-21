from src.theThing.games.crud import *
from src.theThing.cards.crud import *
from src.theThing.players.crud import *
from src.theThing.turn.crud import *
from src.theThing.games.schemas import GameUpdate


async def apply_cac(
    data: dict,
):
    game = get_game(data["game_id"])
    card = get_card(data["card_id"], game.id)
    player = get_player(data["player_id"], game.id)
    panic_card = get_card(data["panic_card_id"], game.id)

    # Remove the panic card from the player
    update_card(CardUpdate(id=data["panic_card_id"], state=0), game.id)
    remove_card_from_player(panic_card.id, player.id, game.id)

    # Get a new card from the deck
    new_card = get_card_from_deck(game.id)
    while new_card.kind == 4:
        update_card(CardUpdate(id=new_card.id, state=0), game.id)
        new_card = get_card_from_deck(game.id)
    give_card_to_player(new_card.id, player.id, game.id)

    # Return the card to the deck
    remove_card_from_player(card.id, player.id, game.id)
    update_card(CardUpdate(id=card.id, state=2), game.id)

    # Update the turn state
    update_turn(game.id, TurnCreate(state=5))

    updated_game = get_game(game.id)
    updated_player = get_player(player.id, game.id)
    return updated_player, updated_game


async def apply_olv(
    data: dict,
):
    game = get_game(data["game_id"])
    cards = [get_card(card_id, game.id) for card_id in data["card_id"]]
    player = get_player(data["player_id"], game.id)
    panic_card = get_card(data["panic_card_id"], game.id)

    # Remove the panic card from the player
    update_card(CardUpdate(id=data["panic_card_id"], state=0), game.id)
    remove_card_from_player(panic_card.id, player.id, game.id)

    # Discard the cards
    for card in cards:
        remove_card_from_player(card.id, player.id, game.id)

    for _ in range(3):
        new_card = get_card_from_deck(game.id)
        while new_card.kind == 4:
            update_card(CardUpdate(id=new_card.id, state=0), game.id)
            new_card = get_card_from_deck(game.id)
        give_card_to_player(new_card.id, player.id, game.id)

    # Update the turn state
    update_turn(game.id, TurnCreate(state=3))

    updated_game = get_game(game.id)
    updated_player = get_player(player.id, game.id)
    return updated_player, updated_game


async def apply_hac(game, attacker, objective, card, obstacle):
    # Remove the panic card from the player
    update_card(CardUpdate(id=card.id, state=0), game.id)
    remove_card_from_player(card.id, attacker.id, game.id)

    # Verify the obstacle to remove
    if obstacle["type"] == "cua" and obstacle["position"] is None:
        update_player(PlayerUpdate(quarantine=0), objective.id, game.id)
        if objective.name == attacker.name:
            message = f"{attacker.name} se jugo hacha para eliminar su cuarentena"
        else:
            message = f"{attacker.name} se jugo hacha para eliminar la cuarentena de {objective.name}"
    elif obstacle["type"] == "ptr" and obstacle["position"] is not None:
        game.obstacles.remove(obstacle["position"])
        update_game(game.id, GameUpdate(obstacles=game.obstacles))
        message = f"{attacker.name} jugo hacha para eliminar una puerta atrancada"

    return message
