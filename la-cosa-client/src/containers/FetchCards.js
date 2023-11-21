import { httpRequest } from "../services/HttpService";

const FetchCards = async ({ onSetHand, gameId, playerId, onSetTablePosition }) => {
  try {
    const statusPlayer = await httpRequest({
      method: "GET",
      service: "game/" + gameId + "/player/" + playerId,
    });
    onSetHand(statusPlayer.json.hand);
    onSetTablePosition(statusPlayer.json["table_position"]);
  } catch (error) {
    console.log(error);
  }
};

export default FetchCards;
