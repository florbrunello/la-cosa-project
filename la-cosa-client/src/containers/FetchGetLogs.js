import { httpRequest } from "../services/HttpService";

const FetchGetLogs = async ({
  gameId
}) => {
  try {
    const response = await httpRequest({
      method: "GET",
      service: "game/"+ gameId + "/get-logs",
    });
    return response; 
  } catch (error) {
    console.log(error);
  }
};

export default FetchGetLogs;
