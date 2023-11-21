import { httpRequest } from "../services/HttpService";

//Make the request to the server
const FetchEndGame = async (data) => {
    const gameId = data.game_id;
    const playerId = data.player_id;
    
    try {
        const response = await httpRequest({
        method: "PUT",
        service: "game/" + gameId + "/player/" + playerId + "/leave",
        });
        return response;
    } catch (error) {
        return error;
    }
};

export default FetchEndGame;


