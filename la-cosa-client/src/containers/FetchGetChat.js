import { httpRequest } from "../services/HttpService";

const FetchGetChat = async ({
  gameId
}) => {
  try {
    const response = await httpRequest({
      method: "GET",
      service: "game/"+ gameId + "/chat",
    });
    return response; 
  } catch (error) {
    console.log(error);
  }
};

export default FetchGetChat;
