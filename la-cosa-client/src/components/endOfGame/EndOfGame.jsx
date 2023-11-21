import React , {useState }from "react";
import { useNavigate, useLocation } from "react-router-dom";
import styles from "./endOfGame.module.css";
import FunctionButton from "../functionButton/FunctionButton";

const EndOfGame = ({socket}) => {
  const navigate = useNavigate();
  const params = useLocation();
  const [results, setResults] = useState({});

  socket.on("game_finished", (data) => setResults(data));
  let gameId = 1; 
  let players = [];
  if (!params.state) {
    gameId = 1;
    players = [];
  } else {
    gameId = params.state.gameId;
    players = params.state.players;
  }

  const goToHome = () => {
    socket.disconnect()
    navigate("/");
  };
  
  return (
    <>
      <div className={styles.endOfGame} data-testid ="text">
        <p className={styles.text}>{results.log}<br />Winners: {results.winners}</p> 
      </div>
      <div className={styles.button}>
        <FunctionButton text={"Abandonar Partida"} onClick={goToHome} />
      </div>
    </>
  );
};

export default EndOfGame;
