import {httpRequest} from "../services/HttpService";

const FetchPlayCard = async ({
    gameId,
    playerId,
    cardId,
    destinationName,
    obstacleType, 
    obstaclePosition
}) => {
    const response = await httpRequest({
        method: "PUT",
        service: "game/play",
        payload: {
            game_id: gameId,
            player_id: playerId,
            card_id: cardId,
            destination_name: destinationName,
            obstacle: {type: obstacleType, position: obstaclePosition}
        },
    });

    return response.status;
};

export default FetchPlayCard;