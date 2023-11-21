import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import Lobby from "../components/game/lobby/Lobby";
import { BrowserRouter } from "react-router-dom";

const mockPlayerData = (
    name = "augusto",
    owner = false
) => ({
    "name": name,
    "owner": owner,
    "id": 2,
    "table_position": 2,
    "role": null,
    "alive": true,
    "quarantine": false,
    "hand": []
});

const mockSocket = {
    disconnect: vi.fn()
}


const gameData = (
    players = [
        {
            "name": "player1",
            "table_position": 1,
            "alive": true,
            "quarantine": false
        },
        {
            "name": "player2",
            "table_position": 1,
            "alive": true,
            "quarantine": false
        },
        {
            "name": "player3",
            "table_position": 1,
            "alive": true,
            "quarantine": false
        },
        {
            "name": "player4",
            "table_position": 1,
            "alive": true,
            "quarantine": false
        }
    ]
) => ({
    "id": 1,
    "name": "game1",
    "min_players": 4,
    "max_players": 12,
    "state": 0,
    "play_direction": null,
    "turn_owner": null,
    "players": players
})



describe("Lobby component", () => {

    test("should render the the host buttons", async () => {

        render(
            <BrowserRouter>
                <Lobby 
                    socket={mockSocket} 
                    player={mockPlayerData("ale",true)} 
                    gameData={gameData()} 
                />
            </BrowserRouter>
        );

        const button1 = screen.getByText('Abandonar Partida');
        const button2 = screen.queryByTestId('Iniciar Partida');

        expect(button1).toBeDefined();
        expect(button2).toBeDefined();
    })


    test("should render the the host buttons", async () => {

        render(
            <BrowserRouter>
                <Lobby 
                    socket={mockSocket} 
                    player={mockPlayerData("ale",false)} 
                    gameData={gameData()} 
                />
            </BrowserRouter>
        );

        const button1 = screen.getByText('Abandonar Partida');
        const button2 = screen.queryByTestId('Iniciar Partida');

        expect(button1).toBeDefined();
        expect(button2).toBeNull();
    })

    test("should render the text when enough players in the lobby and client is the host", async () => {
        render(<BrowserRouter>
                    <Lobby 
                        socket={mockSocket} 
                        player={mockPlayerData("maria", true)} 
                        gameData={gameData()} 
                    />
                </BrowserRouter>
        );
        const text = screen.getByTestId("text-enough-players-and-im-host");
        expect(text).toBeDefined();
    })

    
    test("should render the text when enough players in the lobby and client is not the host", async () => {
        render(<BrowserRouter>
                    <Lobby 
                        socket={mockSocket} 
                        player={mockPlayerData()} 
                        gameData={gameData()} 
                    />
                </BrowserRouter>
        );
        const text = screen.getByTestId("text-enough-players-and-im-not-host");
        expect(text).toBeDefined();
    })

    test("should render the text when not enough players in the lobby for the game to start", async () => {
        render(<BrowserRouter>
                    <Lobby 
                        socket={mockSocket} 
                        player={mockPlayerData()} 
                        gameData={gameData([])} 
                    />
                </BrowserRouter>
        );
        const text = screen.getByTestId("text-not-enough-players");
        expect(text).toBeDefined();
    })
    
    test("should disconnect socket when clicking Abandonar Partida button", async() => {        
        render(
            <BrowserRouter>
                <Lobby 
                    socket={mockSocket} 
                    player={mockPlayerData()} 
                    gameData={gameData([{
                        "name": "player1",
                        "table_position": 1,
                        "alive": true,
                        "quarantine": false
                    }])} 
                />
            </BrowserRouter>
        );

        const goOutGame = vi.fn()
        const button = screen.getByText("Abandonar Partida");
        fireEvent.click(button);
        expect(goOutGame).toBeCalledTimes(0);
    });
});
