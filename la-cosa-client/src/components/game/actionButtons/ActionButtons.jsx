import FunctionButton from "../../functionButton/FunctionButton"

const ActionButtons = ({ 
    DeclareVictory,
    defend, 
    playCard, 
    exchangeCard, 
    player,
    playerId, 
    gameId,
    hasCardToDefend, 
    canPlayCard, 
    hasCardToDefendExchange, 
    actionText 
}) => {
    return (
        <>
            {player.role == 3 && (
                <FunctionButton text={"Declararme Ganador"} onClick={() => DeclareVictory({ gameId, playerId })}/>
            )}
            {hasCardToDefend && (
                <>
                    <FunctionButton text={"Defenderme"} onClick={() => defend(true)}/>
                    <FunctionButton text={"No defenderme"} onClick={() => defend(false)}/>
                </>
            )}
            {canPlayCard.canPlayCard && (
                <FunctionButton text={actionText} onClick={playCard} />
            )}
            {canPlayCard.canExchangeCard && (
                <FunctionButton text={actionText} onClick={() => exchangeCard(false)}/>
            )}
            {hasCardToDefendExchange && (
                <FunctionButton text={"Defenderme del intercambio"} onClick={() => exchangeCard(true)}/>
            )}
        </>
    )
}

export default ActionButtons;