import FetchStartGame from "../../../containers/FetchStartGame";
import FetchEndGame from "../../../containers/FetchEndGame";
import FunctionButton from "../../functionButton/FunctionButton";
import { useState, useEffect} from "react";
import { useNavigate } from "react-router-dom";
import styles from "./lobby.module.css";

const Lobby = ({socket, player, gameData, gameId, playerId}) => {
    const navigate = useNavigate();   
    const [host, setHost] = useState(player.owner);
    const [message, setMessage] = useState("");
    const [error, setError] = useState(false);
    const [data , setData] = useState({}); 
    const [hostHasLeft, setHostHasLeft] = useState(false);
    const [players, setPlayers] = useState([])
    const [minPlayers, setMinPlayers] = useState(false);
    const [text, setText] = useState("")
    
    if (gameData.state === 3) {
        setHostHasLeft(true);
    }

    useEffect(() => {
        const dt = {
            game_id: gameData.id,
            player_name: player.name,
        };
        setData(dt);


    }, [gameData.id, player.name]);


    useEffect(() => {
        setPlayers(gameData.players.map((player) => player.name));
        setMinPlayers(gameData.players.length >= gameData.min_players); 
    }, [gameData.players]);

    const startGame = async (data) => {
        const response = await FetchStartGame(data);
        if (response.status === 200) {
            setError(false);
        } else {
            setMessage(response.json.detail);
            setError(true);
        } 
    }

    const goOutGame = async () => {      
        const data = {
            game_id: gameData.id,
            player_id: player.id,
        }  
        const goOut = await FetchEndGame(data); 
        if(goOut.status === 200){
            setMessage(goOut.json.detail);
        }else{
            setMessage(goOut.json.detail);
            setError(true);
        }
        socket.disconnect(); 
        navigate("/");
    }

    const handleHostLeft = () => {
        socket.disconnect();
        navigate("/");
    }

    return (    
        <div className={styles.body}>
            <div className={styles.fade}>
                {minPlayers ? 
                    (host ? 
                        (<p className={styles.text} data-testid="text-enough-players-and-im-host">
                            Se alcanzó el mínimo de jugadores<br/>
                            Presiona Iniciar Partida<br/>
                            para jugar a La Cosa!
                        </p>)
                    :   (<p className={styles.text} data-testid="text-enough-players-and-im-not-host">
                            Esperando que el host<br/>
                            inicie la partida<br/>
                        </p>)) 
                    
                :   (<p className={styles.text} data-testid="text-not-enough-players">
                        {players.length} jugadores unidos<br/>
                        Esperando {gameData.min_players - players.length} para poder empezar
                    </p>
                    )
                }
            </div>
                {error && <p className={styles.error}>{message}</p>}
            <div className={styles.button} data-testid="buttons" >
                {host && <FunctionButton text={"Iniciar Partida" } onClick={() => startGame(data)}/>}
                {!hostHasLeft && <FunctionButton text={"Abandonar Partida"} onClick={goOutGame}/>}
                {hostHasLeft && <FunctionButton text={"Volver a inicio"} onClick={handleHostLeft}/>} 
            </div>
        </div>   
    )
}

export default Lobby;