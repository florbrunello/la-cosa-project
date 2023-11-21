from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback
from .test_setup import test_db


client = TestClient(app)


@db_session
def test_create_game_success(test_db):
    # Test creating a game with valid data
    game_data = {
        "game": {"name": "Test Game", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)
    assert response.status_code == 201
    assert response.json() == {
        "message": "Partida 'Test Game' creada por 'Test Host' con éxito",
        "game_id": 1,
        "player_id": 1,
    }
    rollback()


@db_session
def test_create_game_empty_name(test_db):
    # Test creating a game with an empty name
    game_data = {
        "game": {"name": "", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)
    assert response.status_code == 422
    assert "El nombre de la partida no puede ser vacío" in response.text
    rollback()


@db_session
def test_create_game_invalid_min_players(test_db):
    # Test creating a game with invalid minimum players
    game_data = {
        "game": {"name": "Test Game", "min_players": 2, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)
    assert response.status_code == 422
    assert "El mínimo de jugadores no puede ser menor a 4" in response.text
    rollback()


@db_session
def test_create_game_invalid_max_players(test_db):
    # Test creating a game with invalid maximum players
    game_data = {
        "game": {"name": "Test Game", "min_players": 4, "max_players": 14},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)
    assert response.status_code == 422
    assert "El máximo de jugadores no puede ser mayor a 12" in response.text
    rollback()


@db_session
def test_create_game_empty_host(test_db):
    # Test creating a game with an empty host name
    game_data = {
        "game": {"name": "TestGame", "min_players": 4, "max_players": 6},
        "host": {"name": ""},
    }
    response = client.post("/game/create", json=game_data)
    assert response.status_code == 422
    assert "El nombre del host no puede ser vacío" in response.text
    rollback()
