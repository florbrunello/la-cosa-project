import { useLocation } from "react-router";
import Core from "./Core";
import { io } from "socket.io-client";

const GameRouter = () => {
    const params = useLocation();
    const { gameId, playerId } = params.state;

    const createSocket = (uri, gameId, playerId) => {
        const socketConfig = {
            transports: ["websocket"],
            query: {
                "Game-Id": gameId,
                "Player-Id": playerId
            },
        };
        const socket = io(uri, socketConfig);
        return socket;
    }
    
    const gameSocket = createSocket("http://localhost:8000/", gameId, playerId);

    return (<Core socket={gameSocket} gameId={gameId} playerId={playerId}/>)
}

export default GameRouter;