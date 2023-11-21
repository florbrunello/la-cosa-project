import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import Game from "../components/game/Game";
import { BrowserRouter } from "react-router-dom";
import MockedSocket from 'socket.io-mock';

const socketMock = new MockedSocket();
const gameContextValue = {
    "id": 1,
    "name": "a",
    "min_players": 4,
    "max_players": 12,
    "state": 1,
    "play_direction": null,
    "turn_owner": null,
    "players": [
        {
        "name": "player1",
        "table_position": 1,
        "alive": true,
        "quarantine": false
        },
        {
            "name": "player1",
            "table_position": 1,
            "alive": true,
            "quarantine": false
        },
        {
            "name": "player1",
            "table_position": 1,
            "alive": true,
            "quarantine": false
        },
        {
            "name": "player1",
            "table_position": 1,
            "alive": true,
            "quarantine": false
        },

    ], 
    "turn": {
        "state": 1,
        "action": 0,
        "player": 1,
        "card": null,
        "target": null
    },
    "obstacles": []
};

const playerContextValue = {
    "name": "game1",
    "owner": false,
    "id": 2,
    "table_position": 2,
    "role": null,
    "alive": true,
    "quarantine": false,
    "hand": []
}

const obstacles = []

describe("Game component", () => {
    test("should render Game component when game state is equal to 1",  () => {

        render(<BrowserRouter>
                <Game socket={socketMock} player={playerContextValue} gameData={gameContextValue} gameId={1}></Game>
            </BrowserRouter>
        )
        expect(screen.getByTestId("game")).toBeDefined();
    })
})