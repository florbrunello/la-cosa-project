import { httpRequest } from "../services/HttpService";

//Make the request to the server
export const FetchJoinGame = async (data) => {
    try {
      const response = await httpRequest({
        method: "POST",
        service: "game/join",
        payload: data,
      });
      return response;
    } catch (error) {
      return error; 
    }
  };
  