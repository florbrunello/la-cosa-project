import { httpRequest } from "../services/HttpService";

const FetchData = async ({ onSetGameData, onSetPlayers, gameId }) => {
  try {
    const apiData = await httpRequest({
      method: "GET",
      service: "game/" + gameId,
    });
    onSetGameData(apiData.json);
    onSetPlayers(apiData.json.players);
  } catch (error) {
    console.log(error);
  }
};

export default FetchData;
