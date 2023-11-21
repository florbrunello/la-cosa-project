import { httpRequest } from "../services/HttpService";

const FetchPlayer = async ({setPlayer, gameId, playerId }) => {
  try {
    const response = await httpRequest({
      method: "GET",
      service: "game/" + gameId + "/player/" + playerId,
    });
    setPlayer(response.json);
  } catch (error) {
    console.log(error);
  }
};

export default FetchPlayer;


