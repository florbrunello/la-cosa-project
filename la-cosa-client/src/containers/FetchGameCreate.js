import { httpRequest } from "../services/HttpService";

//Make the request to the server with data from form
export const FetchCreateGame = async (data) => {
    try {
      const response = await httpRequest({
        method: "POST",
        service: "game/create",
        payload: data,
      });
      return response;
    } catch (error) {
      return error; 
    }
  };