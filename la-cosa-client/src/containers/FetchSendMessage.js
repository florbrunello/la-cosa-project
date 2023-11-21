import { httpRequest } from "../services/HttpService";

const FetchSendMessage = async ({gameId,data}) => {
    console.log("dataa",data)
    

  try {
    const response = await httpRequest({
      method: "PUT",
      service: "game/"+ gameId + "/send-message",
      payload: data,
    });
    return response; 
  } catch (error) {
    console.log(error);
  }
};

export default FetchSendMessage;

