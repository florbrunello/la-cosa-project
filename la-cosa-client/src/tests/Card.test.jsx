import { beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import Card from "../components/game/card/Card";
import { GameContext, CardSelectedContext, SetCardSelectedContext, TurnOwnerContext } from "../components/game/Game";


const props = {
    cardId: 1,
    code: "lla",
    tablePosition: 1
};
const props2 = {
    cardId: 2,
    code: "lla",
    tablePosition: 1
};
const props3 = {
    cardId: 3,
    code: "lla",
    tablePosition: 1
};

const turn = (
    state, 
    cardCode,
    destinationPlayer,
    owner
) => ({
    "owner": owner,
    "played_card": {
        "id": 4,
        "code": cardCode,
        "number_in_card": 8,
        "kind":1
    },
    "destination_player": destinationPlayer,
    "destination_player_exchange": "ale",
    "response_card": null,
    "state": state,
});

describe('Component Card', () => {

    test('should render a card', async () => {
        
        const setCardSelected= vi.fn();
        const cardsSelected = [];
        const setCardsSelected = vi.fn();
        const playedCard = {};
        render(
            <Card
                cardId = {1}
                code = "lla"
                number_in_card = {1}
                kind = {1}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={1}
                tablePosition={1}
                turn={turn(0, null, null)}
                cardSelected={{}}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
        );
        const card = screen.getByTestId("card-1");
        expect(card).toBeDefined();    
        expect(setCardSelected).toHaveBeenCalledTimes(0);
        fireEvent.click(card);
        expect(setCardSelected).toHaveBeenCalledTimes(0);

    });

    test('should call setCardSelected when click on card on turn state 1', async () => {
        const turn_1 = turn(1, null, null, 1);//state 1
        const setCardSelected= vi.fn();
        const cardsSelected = [];
        const setCardsSelected = vi.fn();
        const playedCard = {};
        render(<>
            <Card
                cardId = {1}
                code = "lla"
                number_in_card = {2}
                kind = {1}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={1}
                tablePosition={1}
                turn={turn_1}
                cardSelected={{}}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
            <Card
                cardId = {2}
                code = "cdl"
                number_in_card = {3}
                kind = {1}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={1}
                tablePosition={1}
                turn={turn_1}
                cardSelected={{}}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
            <Card
                cardId = {3}
                code = "ndb"
                number_in_card = {3}
                kind = {2}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={1}
                tablePosition={1}
                turn={turn_1}
                cardSelected={{cardId:3}}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
        </>);
        
        const card1 = screen.getByTestId("card-1");        
        const card2 = screen.getByTestId("card-2");        
        const card3 = screen.getByTestId("card-3");        
        fireEvent.click(card1);
        fireEvent.click(card1);
        expect(setCardSelected).toHaveBeenCalledTimes(2);
        expect(setCardSelected).toHaveBeenCalledWith({ cardId:1, code:"lla", kind:1 });
        fireEvent.click(card2);
        expect(setCardSelected).toHaveBeenCalledTimes(3);
        expect(setCardSelected).toHaveBeenCalledWith({ cardId:2, code:"cdl", kind:1 });
        fireEvent.click(card3);
        expect(setCardSelected).toHaveBeenCalledTimes(4);
        expect(setCardSelected).toHaveBeenCalledWith({});
    });

    test('should call setCardSelected when click on card on turn state 3', async () => {
        
        const turn_3 = turn(3, null, null, 1);//state 1
        const setCardSelected= vi.fn();
        const cardsSelected = [];
        const setCardsSelected = vi.fn();
        const playedCard = {};
        render(<>
            <Card
                cardId = {1}
                code = "lla"
                number_in_card = {2}
                kind = {1}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={1}
                tablePosition={1}
                turn={turn_3}
                cardSelected={{}}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
            <Card
                cardId = {2}
                code = "cdl"
                number_in_card = {3}
                kind = {3}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={3}
                tablePosition={1}
                turn={turn_3}
                cardSelected={{}}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
            <Card
                cardId = {3}
                code = "ndb"
                number_in_card = {3}
                kind = {2}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={1}
                tablePosition={1}
                turn={turn_3}
                cardSelected={{cardId:3}}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
        </>);
        
        const card1 = screen.getByTestId("card-1");        
        const card2 = screen.getByTestId("card-2");        
        const card3 = screen.getByTestId("card-3");        
        fireEvent.click(card1);
        fireEvent.click(card1);
        expect(setCardSelected).toHaveBeenCalledTimes(2);
        expect(setCardSelected).toHaveBeenCalledWith({ cardId:1, code:"lla", kind:1 });
        fireEvent.click(card2);
        expect(setCardSelected).toHaveBeenCalledTimes(3);
        expect(setCardSelected).toHaveBeenCalledWith({ cardId:2, code:"cdl", kind:3 });
        fireEvent.click(card3);
        expect(setCardSelected).toHaveBeenCalledTimes(4);
        expect(setCardSelected).toHaveBeenCalledWith({});
    });

    test('should call setCardSelected when click on card on turn state 4', async () => {
        
        const turn_4 = turn(4, null, "ale", 1);//state 1
        const setCardSelected= vi.fn();
        const cardsSelected = [];
        const setCardsSelected = vi.fn();
        const playedCard = {};
        render(<>
            <Card
                cardId = {1}
                code = "lla"
                number_in_card = {2}
                kind = {1}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={1}
                tablePosition={1}
                turn={turn_4}
                cardSelected={{}}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
            <Card
                cardId = {2}
                code = "cdl"
                number_in_card = {3}
                kind = {3}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={3}
                tablePosition={1}
                turn={turn_4}
                cardSelected={{}}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
            <Card
                cardId = {3}
                code = "ndb"
                number_in_card = {3}
                kind = {2}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={1}
                tablePosition={1}
                turn={turn_4}
                cardSelected={{cardId:3}}
                cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
            />
        </>);
        
        const card1 = screen.getByTestId("card-1");        
        const card2 = screen.getByTestId("card-2");        
        const card3 = screen.getByTestId("card-3");        
        fireEvent.click(card1);
        fireEvent.click(card1);
        expect(setCardSelected).toHaveBeenCalledTimes(2);
        expect(setCardSelected).toHaveBeenCalledWith({ cardId:1, code:"lla", kind:1 });
        fireEvent.click(card2);
        expect(setCardSelected).toHaveBeenCalledTimes(3);
        expect(setCardSelected).toHaveBeenCalledWith({ cardId:2, code:"cdl", kind:3 });
        fireEvent.click(card3);
        expect(setCardSelected).toHaveBeenCalledTimes(4);
        expect(setCardSelected).toHaveBeenCalledWith({});
    });

    test('should call setCardsSelected when click on cards on turn state 6 when the played card is cac', async () => {
        
        const turn_6 = turn(6, null, null, 1);//state 1
        const setCardSelected= vi.fn();

        const cardsSelectedStatus= (
            code1 = "cac"
        ) => ({
            cardsSelected : [1], 
            setCardsSelected: vi.fn(), 
            playedCard : {code: code1}
        });

        const cardsSelectedStat = cardsSelectedStatus();
        render(<>
            <Card
                cardId = {1}
                code = "lla"
                number_in_card = {2}
                kind = {1}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={1}
                tablePosition={1}
                turn={turn_6}
                cardSelected={{}}
                cardsSelectedStatus={cardsSelectedStat}
            />
            <Card
                cardId = {2}
                code = "cdl"
                number_in_card = {3}
                kind = {3}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={3}
                tablePosition={1}
                turn={turn_6}
                cardSelected={{}}
                cardsSelectedStatus={cardsSelectedStat}
            />
        </>);
        
        const card1 = screen.getByTestId("card-1"); 
        const card2 = screen.getByTestId("card-2");            
        fireEvent.click(card1);

        expect(cardsSelectedStat.setCardsSelected).toHaveBeenCalledTimes(1);
        expect(cardsSelectedStat.setCardsSelected).toHaveBeenCalledWith([]);
        fireEvent.click(card2);
        expect(cardsSelectedStat.setCardsSelected).toHaveBeenCalledTimes(2);
        expect(cardsSelectedStat.setCardsSelected).toHaveBeenCalledWith([2]);
    });

    test('should call setCardsSelected when click on cards on turn state 6 when the played card is olv', async () => {
        
        const turn_6 = turn(6, null, null, 1);//state 1
        const setCardSelected= vi.fn();

        const cardsSelectedStatus = {
            cardsSelected : [3,4], 
            setCardsSelected: vi.fn(), 
            playedCard : {code: "olv"}
        };

        const cardsSelectedStatus2 = {
            cardsSelected : [11,10,4], 
            setCardsSelected: vi.fn(), 
            playedCard : {code: "olv"}
        };



        render(<>
            <Card
                cardId = {1}
                code = "lla"
                number_in_card = {2}
                kind = {4}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={1}
                tablePosition={1}
                turn={turn_6}
                cardSelected={{}}
                cardsSelectedStatus={cardsSelectedStatus}
            />
            <Card
                cardId = {2}
                code = "cdl"
                number_in_card = {3}
                kind = {3}
                setCardSelected={setCardSelected}
                playerName={"ale"}
                playerRole={3}
                tablePosition={1}
                turn={turn_6}
                cardSelected={{}}
                cardsSelectedStatus={cardsSelectedStatus2}
            />
        </>);
        
        const card1 = screen.getByTestId("card-1"); 
        const card2 = screen.getByTestId("card-2");            
        
        fireEvent.click(card1);
        expect(setCardSelected).toHaveBeenCalledTimes(1);
        expect(cardsSelectedStatus.setCardsSelected).toHaveBeenCalledTimes(1);
        expect(cardsSelectedStatus.setCardsSelected).toHaveBeenCalledWith([3,4,1]);
        fireEvent.click(card2);
        console.log(cardsSelectedStatus2)
        expect(cardsSelectedStatus2.setCardsSelected).toHaveBeenCalledTimes(1);
        expect(cardsSelectedStatus2.setCardsSelected).toHaveBeenCalledWith([11,10,2]);
    });

});
