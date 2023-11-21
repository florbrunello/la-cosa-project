import { httpRequest } from "../services/HttpService";

//Make the request to the server
const FetchStartGame = async (data) => {
  try {
    const response = await httpRequest({
      method: "POST",
      service: "game/start",
      payload: data,
    });
    return response;
  } catch (error) {
    return error;
  }
};

export default FetchStartGame;
