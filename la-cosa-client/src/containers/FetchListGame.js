import { httpRequest } from "../services/HttpService";

//Make the request to the server
const FetchListGame = async () => {
  try {
    const response = await httpRequest({
      method: "GET",
      service: "game/list",
    });
    return response;
  } catch (error) {
    return error;
  }
};

export default FetchListGame;
