import { httpRequest } from '../services/HttpService'
    
const FetchStealCard = async ( data ) => {
    try {
        const response = await httpRequest({
            method: 'PUT', 
            service: 'game/steal', 
            payload: data
        });
        return response;
    } catch (error) {
        console.log(error);
    }
};

export default FetchStealCard;