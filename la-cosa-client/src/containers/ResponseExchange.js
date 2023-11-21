import {httpRequest} from "../services/HttpService";

const ResponseExchange = async ({
    gameId,
    playerId,
    cardId,
    defenseCardId
}) => {
    const response = await httpRequest({
        method: "PUT",
        service: "game/response-exchange",
        payload: {
            game_id: gameId,
            defending_player_id: playerId,
            exchange_card_id: cardId,
            defense_card_id: defenseCardId
        },
    });

    return response.status;
};

export default ResponseExchange;