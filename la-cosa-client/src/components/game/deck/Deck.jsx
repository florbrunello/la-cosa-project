import { useState, useEffect } from 'react';
import FetchStealCard from '../../../containers/FetchStealCard';
import style from '../deck/deck.module.css';

const Deck = ({
    player,
    playDirection,
    gameId,
    turnOwner,
    turnState,
    cardSelected,
    discardState,
    setPlayerSelected,
    setCardLifted,
    setInstructionReciever
}) => {

    const isTurnOwner = (turnOwner === player.table_position); //calculate if the player is the owner of the turn


    const [message, setMessage] = useState('');
    const [clicked, setClicked] = useState(false);
    
    const styleDeck =  (turnState === 0 && player.table_position == turnOwner) ? style.img : style.img2;
    const arrowClassName = playDirection ? "arrowRight" : "arrowLeft";

    useEffect(()=>{
        setMessage('');
        setClicked(false);
        setCardLifted(false);
    },[turnOwner])


    const liftCard = async () => {
        switch (turnState) {
            case 0: //lifting card
                setInstructionReciever(player.name);
                if (player.hand.length >= 5){
                    setMessage('Tienes el maximo de cartas ya!');
                }
                else if (player.table_position == turnOwner && !clicked) {
                    const data = {game_id: gameId, player_id: player.id}
                    const response = await FetchStealCard(data)
                    if(response.status === 200) {
                        setMessage(response.detail);
                        setClicked(true);
                        setCardLifted(true);
                    }
                    else {
                        setMessage(response.detail);
                    }
                }
                else if (player.table_position == turnOwner && clicked) {
                    setMessage('Ya robaste una carta');
                }
                else {
                    setMessage('No es tu turno');
                }
                break;
            default:
                return 0;
                }
    }

    const discardCard = async () => {
        if (isTurnOwner && cardSelected.cardId !== undefined && turnState === 1 && cardSelected.kind !== 4) {    
            discardState.setDiscard(!discardState.discard);
            setPlayerSelected({});
        }
    }

    const roles = ["Humano", "Infectado", "La Cosa!"]

    return (
        <>
            <div className={style.container}>
                <div>
                    <div className={style[arrowClassName]}>
                        <img src="../../../src/img/arrow.png"/>
                    </div>
                    <p>Eres {roles[player.role - 1]}</p>
                    {player.quarantine > 0 && (<p>Estás en cuarentena!<br/>Turnos restantes para dejar de estarlo: {player.quarantine}</p>)}
                </div>
                <div className={style.cardDeck} onClick={liftCard} data-testid="deck">
                    <img src={`../../../src/img/atk.png`} className={styleDeck} />
                </div>
                <div className={style.cardDeck} onClick={discardCard} data-testid="discard">
                    <img src={`../../../src/img/tachoBasura.png`}  className={style.trash} />
                </div>
            </div>
        </>
    );
};

export default Deck;
