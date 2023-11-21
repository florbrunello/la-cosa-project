import { httpRequest } from "../services/HttpService";

export const getResults = async(game_id) => {
    try {
        const response = await httpRequest({
        method: "GET",
        service: `game/${game_id}/results`,
        });
        return response;
    } catch (error) {
        return error; 
    }
};