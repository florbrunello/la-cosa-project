from src.theThing.games.models import Game
from pony.orm import db_session


def load_data_for_test():
    games = [
        ("Uno", 4, 12, None),
        ("Dos", 2, 10, None),
        ("Tres", 3, 8, "securepassword"),
    ]

    with db_session:
        for name, min_players, max_players, password in games:
            if not password:
                Game(
                    name=name, min_players=min_players, max_players=max_players
                )
            else:
                Game(
                    name=name,
                    min_players=min_players,
                    max_players=max_players,
                    password=password,
                )
