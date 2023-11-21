import { describe, expect, test, vi } from "vitest";
import { render, screen} from '@testing-library/react';
import Hand from "../components/game/hand/Hand";

const mockPlayerData = (
    name = "augusto",
    codes = ["lla", "lla", "lla", "wsk"]
) => ({
    "name": name,
    "owner": false,
    "id": 2,
    "table_position": 2,
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

const cardSelected = (
    cardId = 1,
    code = "lla",
    kind = 1,
)=>(
    {
        cardId: cardId,
        code: code,
        kind: kind
    }
);

const cardsSelected = [1,2,3];
const setCardsSelected = vi.fn();
const playedCard = {};

describe('PlayerHand', () => {

    test('should render players hand', async () => {

        const setCardSelected = vi.fn();
        const defendCard = vi.fn();

        render(      
            <Hand
                player={mockPlayerData()}
                turn={turn(1,null)}
                setCardSelected={setCardSelected}
                defendCard={defendCard}
                cardSelected={cardSelected()}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
        );

        const hand = screen.getByTestId("hand");
        expect(hand).toBeDefined()
    });
    
    test('should render the cards in the hand', async () => {
        const setCardSelected = vi.fn();
        const defendCard = vi.fn();
        render(      
            <Hand
                player={mockPlayerData()}
                turn={turn(1,null)}
                setCardSelected={setCardSelected}
                defendCard={defendCard}
                cardSelected={cardSelected()}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
        );
            
        const hand = screen.getByTestId("hand");
        const cards = screen.getAllByTestId(/card-/);
        expect(cards).toHaveLength(4);  
    });

    test('should verify if the player can not defend the lla card', async () => {
        const playerData = mockPlayerData("ale");
        const turn2 = turn(2, "lla", "ale");

        const setCardSelected = vi.fn();
        const defendCard = vi.fn();
        render(      
            <Hand
                player={playerData}
                turn={turn2}
                setCardSelected={setCardSelected}
                defendCard={defendCard}
                cardSelected={cardSelected()}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
        );

        expect(defendCard).toHaveBeenCalledTimes(1);
        expect(defendCard).toHaveBeenCalledWith(null);
        expect(setCardSelected).toHaveBeenCalledTimes(0);
    });

    test('should verify if the player can defend the lla card', async () => {
        const playerData = mockPlayerData("ale", ["lla", "ndb", "lla", "lla"]);
        const turn2 = turn(2, "lla", "ale");

        const setCardSelected = vi.fn();
        const defendCard = vi.fn();
        render(      
            <Hand
                player={playerData}
                turn={turn2}
                setCardSelected={setCardSelected}
                defendCard={defendCard}
                cardSelected={cardSelected()}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
        );

        expect(defendCard).toHaveBeenCalledTimes(1);
        expect(defendCard).toHaveBeenCalledWith(2);
        expect(setCardSelected).toHaveBeenCalledTimes(1);
        expect(setCardSelected).toHaveBeenCalledWith({cardId: 2, code: 'ndb', kind: 2});
    });

    test('should verify if the player can not defend the cdl card', async () => {
        const playerData = mockPlayerData("ale");
        const turn2 = turn(2, "cdl", "ale");
        const setCardSelected = vi.fn();
        const defendCard = vi.fn();

        render(      
            <Hand
                player={playerData}
                turn={turn2}
                setCardSelected={setCardSelected}
                defendCard={defendCard}
                cardSelected={cardSelected()}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
        );

        expect(defendCard).toHaveBeenCalledTimes(1);
        expect(defendCard).toHaveBeenCalledWith(null);
        expect(setCardSelected).toHaveBeenCalledTimes(0);
    });

    test('should verify if the player can defend the cdl card', async () => {
        const playerData = mockPlayerData("ale", ["lla", "ndb", "aeb", "lla"]);
        const turn2 = turn(2, "cdl", "ale");

        const setCardSelected = vi.fn();
        const defendCard = vi.fn();
        render(      
            <Hand
                player={playerData}
                turn={turn2}
                setCardSelected={setCardSelected}
                defendCard={defendCard}
                cardSelected={cardSelected()}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
        );

        expect(defendCard).toHaveBeenCalledTimes(1);
        expect(defendCard).toHaveBeenCalledWith(3);
        expect(setCardSelected).toHaveBeenCalledTimes(1);
        expect(setCardSelected).toHaveBeenCalledWith({cardId: 3, code: 'aeb', kind: 2});
    });

    test('should verify if the player can not defend the wsk card', async () => {
        const playerData = mockPlayerData("ale");
        const turn2 = turn(2, "wsk", "ale");
        const setCardSelected = vi.fn();
        const defendCard = vi.fn();

        render(      
            <Hand
                player={playerData}
                turn={turn2}
                setCardSelected={setCardSelected}
                defendCard={defendCard}
                cardSelected={cardSelected()}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
        );

        expect(defendCard).toHaveBeenCalledTimes(1);
        expect(defendCard).toHaveBeenCalledWith(null);
        expect(setCardSelected).toHaveBeenCalledTimes(0);
    });
});