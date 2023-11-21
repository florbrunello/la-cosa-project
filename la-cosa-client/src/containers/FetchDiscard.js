import { httpRequest } from '../services/HttpService'
    
const FetchDiscard = async ({
    gameId,
    playerId,
    cardId,
    destinationName
    }) => {
    try {
        const response = await httpRequest({
            method: 'PUT', 
            service: 'game/discard', 
            payload: { 
                game_id: gameId,
                player_id: playerId,
                card_id: cardId,
                destination_name: destinationName} 
        });
        return response;
    } catch (error) {
        console.log(error);
    }
};

export default FetchDiscard;