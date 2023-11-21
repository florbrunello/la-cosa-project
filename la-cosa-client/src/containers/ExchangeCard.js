import {httpRequest} from "../services/HttpService";

const ExchangeCard = async ({
    gameId,
    playerId,
    cardId,
}) => {
    const response = await httpRequest({
        method: "PUT",
        service: "game/exchange",
        payload: {
            game_id: gameId,
            player_id: playerId,
            card_id: cardId,
        },
    });

    return response.status;
};

export default ExchangeCard;