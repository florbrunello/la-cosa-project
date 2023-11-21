import { render } from "@testing-library/react";
import { expect, test } from "vitest";
import Table from "../components/game/table/Table";


const mockPlayerData = (
    name = "augusto",
    table_position = 1,
) => ({
    "name": name,
    "owner": false,
    "id": 2,
    "table_position": table_position,
    "role": null,
    "alive": true,
    "quarantine": false,
    "hand": [
        {
        "id": 1,
        "cardId": 1,
        "code": "lla",
        "number_in_card": 1,
        "kind":1
    },{
        "id": 2,
        "code": "lla",
        "number_in_card": 4,
        "kind":1
    },{
        "id": 3,
        "code": "lla",
        "number_in_card": 6,
        "kind":1
    },{
        "id": 4,
        "code": "wsk",
        "number_in_card": 8,
        "kind":1
    }]
});

const turn = {
        "state": 1,
        "action": 0,
        "player": 1,
        "card": null,
        "target": null, 
        "owner": 1
    };


const players = [
    {
        "name": "player1",
        "table_position": 1,
        "alive": true,
        "quarantine": 0,
    },
    {
        "name": "player2",
        "table_position": 2,
        "alive": true,
        "quarantine": 0,
    },        
    {
        "name": "player3",
        "table_position": 3,
        "alive": true,
        "quarantine": 0,
    },
    {
        "name": "player4",
        "table_position": 4,
        "alive": true,
        "quarantine": 0,
    }
];

describe('Table', () => {
    test('should render the players correctly', () => {

        const setPlayerSelected = vi.fn();
        const setDiscard =  vi.fn();
        const discard = false;
        const obstacles = [1];
        const doorSelected = false;
        const setDoorSelected = vi.fn();

        const { getByText } = render(
            <Table  players={players} 
                    player={mockPlayerData()}
                    playerSelectedState={{name: "ale", setPlayerSelected}}
                    cardSelected={{cardId: 1}}
                    discardState={{discard, setDiscard}}
                    turn={turn}
                    obstacles={obstacles}
                    doorSelected={doorSelected}
                    setDoorSelected={setDoorSelected}
                    />                             
        );
    
        players.forEach((player) => {
            const playerName = getByText(player.name);
            expect(playerName).toBeDefined();
        });
    });
  });