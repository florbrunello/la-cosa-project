import { httpRequest } from "../services/HttpService";

const FetchEndTurn = async ({ gameId }) => {
  try {
    const response = await httpRequest({
      method: "PUT",
      service: "turn/finish",
      payload: {game_id: gameId}
    });
    return response; 
  } catch (error) {
    console.log(error);
    return;
  }
};

export default FetchEndTurn;

