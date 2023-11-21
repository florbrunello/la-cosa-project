import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, test } from "vitest";
import Player from "../components/game/player/Player";

const mockPlayerData = (
    name = "augusto",
    tablePosition = 2,
    codes = ["lla", "lla", "lla", "wsk"]
) => ({
    "name": name,
    "owner": false,
    "id": 2,
    "table_position": tablePosition,
    "role": null,
    "alive": true,
    "quarantine": false,
    "hand": [
        {
        "id": 1,
        "cardId": 1,
        "code": codes[0],
        "number_in_card": 1,
        "kind":1
    },{
        "id": 2,
        "code": codes[1],
        "number_in_card": 4,
        "kind":2
    },{
        "id": 3,
        "code": codes[2],
        "number_in_card": 6,
        "kind":2
    },{
        "id": 4,
        "code": codes[3],
        "number_in_card": 8,
        "kind":1
    }]
});

const turn = (
    state, 
    cardCode,
    destinationPlayer
) => ({
    "owner": 3,
    "played_card": {
        "id": 4,
        "code": cardCode,
        "number_in_card": 8,
        "kind":1
    },
    "destination_player": destinationPlayer,
    "response_card": null,
    "state": state,
});

const players = [
    {
        "name": "player1",
        "table_position": 1,
        "alive": true,
        "quarantine": false
    },
    {
        "name": "player2",
        "table_position": 2,
        "alive": true,
        "quarantine": false
    },
    {
        "name": "player3",
        "table_position": 3,
        "alive": true,
        "quarantine": false
    },
    {
        "name": "player4",
        "table_position": 4,
        "alive": true,
        "quarantine": false
    }
];

describe("Player component", () => {
    
    test("should render the player", async () => {

        const player = mockPlayerData("player1");
        const playerSelectedState = {playerSelected: undefined, setPlayerSelected: vi.fn()};
        const cardSelected = {};

        const turn_1 = turn(1, "lla", 2);
        const obstacles = [1];
        const doorSelected = false;
        const setDoorSelected = vi.fn();
        render(<>
            <Player 
                name={"player1"}
                playerData={players.find((p1) => p1.name === "player1")}
                player={player}
                playerSelectedState={playerSelectedState}
                cardSelected={cardSelected}
                players={players}
                setDiscard={vi.fn()}
                turn={turn_1}
                obstacles={obstacles}
                setDoorSelected={setDoorSelected} 
            />
        </>);

        const player_ = screen.getByTestId("player-player1");
        expect(player_).toBeDefined();
    });

    test("should call setPlayerSelected when click on player", async () => {
        const player = mockPlayerData("player1", 1);
        const player2 = mockPlayerData("player2", 2);
        const player3 = mockPlayerData("player3", 3);
        const playerSelectedState = {name: "player1", setPlayerSelected: vi.fn()};
        const cardSelected = {cardId: 1, code:"sos", number_in_card: 1, kind: 1};
        const cardSelected2 = {cardId: 1, code:"wky", number_in_card: 1, kind: 1};

        const turn_1 = turn(1, "sed", null);
        const obstacles = [3];
        const doorSelected = false;
        const setDoorSelected = vi.fn();
        render(<>
            <Player 
                name={"player1"}
                playerData={players.find((p1) => p1.name === "player1")}
                player={player}
                playerSelectedState={playerSelectedState}
                cardSelected={cardSelected}
                players={players}
                setDiscard={vi.fn()}
                turn={turn_1}
                obstacles={obstacles}
                setDoorSelected={setDoorSelected} 
            />
            <Player 
                name={"player2"}
                playerData={players.find((p1) => p1.name === "player2")}
                player={player2}
                playerSelectedState={playerSelectedState}
                cardSelected={cardSelected}
                players={players}
                setDiscard={vi.fn()}
                turn={turn_1}
                obstacles={obstacles}
                setDoorSelected={setDoorSelected} 
            />
            <Player 
                name={"player3"}
                playerData={players.find((p1) => p1.name === "player3")}
                player={player3}
                playerSelectedState={playerSelectedState}
                cardSelected={cardSelected2}
                players={players}
                setDiscard={vi.fn()}
                turn={turn_1}
                obstacles={obstacles}
                setDoorSelected={setDoorSelected} 
            />
        </>);
        const player_1 = screen.getByTestId("player-player1");        
        const player_2 = screen.getByTestId("player-player2");        
        const player_3 = screen.getByTestId("player-player3");      
        
        fireEvent.click(player_1);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledTimes(4);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledWith({});
        fireEvent.click(player_2);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledTimes(5);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledWith({name: "player2"});
        fireEvent.click(player_3);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledTimes(6);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledWith({});
    });

    test("should call setPlayerSelected when click on player", async () => {
        const player = mockPlayerData("player1", 1);
        const player2 = mockPlayerData("player2", 2);
        const player3 = mockPlayerData("player3", 3);
        const player4 = mockPlayerData("player4", 4);
        const playerSelectedState = {name: "player1", setPlayerSelected: vi.fn()};
        const cardSelected = {cardId: 1, code:"lla", number_in_card: 1, kind: 1};
        const cardSelected2 = {cardId: 2, code:"sed", number_in_card: 1, kind: 1};
        const cardSelected3 = {cardId: 3, code:"sos", number_in_card: 1, kind: 1};
        const cardSelected4 = {cardId: 3, code:"cdl", number_in_card: 1, kind: 1};

        const turn_1 = turn(1, null, null);
        const obstacles = [3];
        const doorSelected = false;
        const setDoorSelected = vi.fn();
        render(<>
            <Player 
                name={"player1"}
                playerData={players.find((p1) => p1.name === "player1")}
                player={player}
                playerSelectedState={playerSelectedState}
                cardSelected={cardSelected}
                players={players}
                setDiscard={vi.fn()}
                turn={turn_1}
                obstacles={obstacles}
                setDoorSelected={setDoorSelected} 
            />
            <Player 
                name={"player2"}
                playerData={players.find((p1) => p1.name === "player2")}
                player={player2}
                playerSelectedState={playerSelectedState}
                cardSelected={cardSelected2}
                players={players}
                setDiscard={vi.fn()}
                turn={turn_1}
                obstacles={obstacles}
                setDoorSelected={setDoorSelected} 
            />
            <Player 
                name={"player3"}
                playerData={players.find((p1) => p1.name === "player3")}
                player={player3}
                playerSelectedState={playerSelectedState}
                cardSelected={cardSelected3}
                players={players}
                setDiscard={vi.fn()}
                turn={turn_1}
                obstacles={obstacles}
                setDoorSelected={setDoorSelected} 
            />
            <Player 
                name={"player4"}
                playerData={players.find((p1) => p1.name === "player4")}
                player={player4}
                playerSelectedState={playerSelectedState}
                cardSelected={cardSelected3}
                players={players}
                setDiscard={vi.fn()}
                turn={turn_1}
                obstacles={obstacles}
                setDoorSelected={setDoorSelected} 
            />
        </>);
        const player_1 = screen.getByTestId("player-player1");        
        const player_2 = screen.getByTestId("player-player2");        
        const player_3 = screen.getByTestId("player-player3");      
        const player_4 = screen.getByTestId("player-player4");      
        
        fireEvent.click(player_1);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledTimes(5);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledWith({});
        fireEvent.click(player_2);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledTimes(6);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledWith({name: "player2"});
        fireEvent.click(player_3);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledTimes(6);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledWith({});
        fireEvent.click(player_4);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledTimes(7);
        expect(playerSelectedState.setPlayerSelected).toHaveBeenCalledWith({});

    });

    // test("should player selected have diferent style properties than not seleted", async () => {
    //     const player1 = screen.getByTestId("player-a");        
    //     const player2 = screen.getByTestId("player-a2");        
    //     const player3 = screen.getByTestId("player-a3");      

    //     expect(window.getComputedStyle(player1)._values["background-color"]).not.toEqual(window.getComputedStyle(player2)._values["background-color"]);
    //     expect(window.getComputedStyle(player3)._values["background-color"]).toEqual(window.getComputedStyle(player2)._values["background-color"]);
    // });

})
