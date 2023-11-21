import { useEffect, useRef, useState } from "react";
import Game from "../components/game/Game";
import Lobby from "../components/game/lobby/Lobby";
import EndOfGame from "../components/endOfGame/EndOfGame";
import GameAborted from "../components/game/lobby/gameAborted/GameAborted";

const Core = ({socket, gameId, playerId}) => {
    // gameState 0 -> lobby, 1 -> game, 2 -> end-of-game, 3 -> aborted
    const [gameData, setGameData] = useState({});
    const [playerData, setPlayerData] = useState({});

    socket.on("connect", () => console.log("websocket connected"));
    socket.on("disconnect", (reason) =>  console.log("socket se desconecto por", reason));
    socket.on("game_status", (data) => setGameData(data));
    socket.on("player_status", (data) => setPlayerData(data));

    switch(gameData.state) {
        case 0:
            return (<Lobby socket={socket} player={playerData} gameData={gameData} gameId={gameId} playerId={playerId}/>)
        case 1:
            return (<Game socket={socket} player={playerData} gameData={gameData} gameId={gameId} playerId={playerId}/>);

        case 2:
            return (<EndOfGame socket={socket}/>)
        
        case 3:
            return (<GameAborted socket={socket}/>)
            
        default:
            return (<div><h1>Cargando...</h1></div>)
    
    }
}

export default Core;