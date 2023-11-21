import { describe, test, expect, vi } from 'vitest';
import { render, screen, fireEvent} from "@testing-library/react";
import Deck from '../components/game/deck/Deck';

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

describe('Trash Icon', () => {
 
    test("should call a function when clicking on the trash icon when is turn owner", () => {
        
        const discard = false;
        const setDiscard = vi.fn();
        const setPlayerSelected = vi.fn();
        const cardSelected = {
            cardId: 1,
        }
        const setCardLifted = vi.fn();
        const setInstructionReciever = vi.fn();
        render(            

            <Deck player={mockPlayerData()} 
                playDirection={1} 
                gameId={1}
                turnOwner={1}
                turnState={1}
                cardSelected={{cardId: 1}}
                discardState={{discard, setDiscard}}
                setPlayerSelected={setPlayerSelected}
                setCardLifted={setCardLifted}
                setInstructionReciever={setInstructionReciever}
            />
        )

        const trashIcon = screen.getByTestId("discard");
        fireEvent.click(trashIcon);      
        expect(discard).toBeDefined;
        expect(setDiscard).toHaveBeenCalledTimes(1);
        expect(setPlayerSelected).toHaveBeenCalledTimes(1);
    });

    test("should not call a function when clicking on the trash icon when is not turn owner", () => {
        const discard = false;
        const setDiscard = vi.fn();
        const setPlayerSelected = vi.fn();
        const setCardLifted = vi.fn();
        const setInstructionReciever = vi.fn();
        render(            
            <Deck player={mockPlayerData()} 
                playDirection={1} 
                gameId={1}
                turnOwner={1}
                turnState={1}
                cardSelected={{cardId: 1}}
                discardState={{discard, setDiscard}}
                setPlayerSelected={setPlayerSelected}
                setCardLifted={setCardLifted}
                setInstructionReciever={setInstructionReciever}
                />
        )

        const trashIcon = screen.getByTestId("discard");
        expect(trashIcon).toBeDefined;

        fireEvent.click(trashIcon);      
        expect(setDiscard).toBeCalledTimes(1);
        expect(setDiscard).toBeCalledWith(true);
        expect(setPlayerSelected).toHaveBeenCalledTimes(1);
        
        fireEvent.click(trashIcon);      
        expect(setDiscard).toBeCalledTimes(2);
        expect(setPlayerSelected).toHaveBeenCalledTimes(2);
    });
    
    test("should not call a function when clicking on the trash icon when is not turn owner", () => {
        const discard = false;
        const setDiscard = vi.fn();
        const setPlayerSelected = vi.fn();
        const setCardLifted = vi.fn();
        const setInstructionReciever = vi.fn();
        render(            
            <Deck player={mockPlayerData()} 
                playDirection={1} 
                gameId={1}
                turnOwner={2}
                turnState={1}
                cardSelected={{cardId: 1}}
                discardState={{discard, setDiscard}}
                setPlayerSelected={setPlayerSelected}
                setCardLifted={setCardLifted}
                setInstructionReciever={setInstructionReciever}
            />
        )

        const trashIcon = screen.getByTestId("discard");
        expect(trashIcon).toBeDefined;

        fireEvent.click(trashIcon);      
        expect(setDiscard).toBeCalledTimes(0);
        expect(setPlayerSelected).toHaveBeenCalledTimes(0);
    });
});

describe('Deck', () => {
    test("should render the deck correctly", () => {
        const discard = false;
        const setDiscard = vi.fn();
        const setPlayerSelected = vi.fn();
        const setCardLifted = vi.fn();
        const setInstructionReciever = vi.fn();
        render(            
            <Deck player={mockPlayerData()} 
                playDirection={1} 
                gameId={1}
                turnOwner={1}
                turnState={0}
                cardSelected={{cardId: 1}}
                discardState={{discard, setDiscard}}
                setPlayerSelected={setPlayerSelected}
                setCardLifted={setCardLifted}
                setInstructionReciever={setInstructionReciever}
            />
        )

        const deck = screen.getByTestId("deck");
        expect(deck).toBeDefined();
        fireEvent.click(deck);
        expect(setCardLifted).toHaveBeenCalledTimes(1);
    });
});
