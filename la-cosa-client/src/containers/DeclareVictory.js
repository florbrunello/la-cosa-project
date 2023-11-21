import { httpRequest } from "../services/HttpService";

const DeclareVictory = async({gameId, playerId}) => {
    
    const data = {game_id: gameId, player_id: playerId}
    try {
        const response = await httpRequest({
        method: "PUT",
        service: `game/declare-victory`,
        payload: data,
        });
        return response;
    } catch (error) {
        return error; 
    }
};


export default DeclareVictory;