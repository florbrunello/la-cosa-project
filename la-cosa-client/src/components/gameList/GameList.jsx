import { useNavigate } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import FetchListGame from "../../containers/FetchListGame";
import FunctionButton from "../functionButton/FunctionButton";
import styles from "./gameList.module.css";

const GameList = () => {
  const navigate = useNavigate();
  const [list, setList] = useState([]);
  const timerIdRef = useRef(null);
  const [isPollingEnabled, setIsPollingEnabled] = useState(true);
 
  //Polling to get the list of games
  useEffect(() => {
    const pollingCallback = () => {
      FetchListGame().then((response) => {
        console.log(response);
        if (!response.ok) {
          setIsPollingEnabled(false);
        } else {
          setList(response.json);
        }
      });
    };

    const startPolling = () => {
      pollingCallback(); 
      // Polling every 2 seconds
      timerIdRef.current = setInterval(pollingCallback, 2000);
    };

    const stopPolling = () => {
      clearInterval(timerIdRef.current);
    };

    if (isPollingEnabled) {
      startPolling();
    } else {
      stopPolling();
    }

    return () => {
      stopPolling();
    };
  }, [isPollingEnabled]);

  const goToForm = (gameId) =>
    () => {
        console.log(gameId)
      navigate("/game-join-form", { state: { gameId } });
    };

  const gotoMenu = () => {
      navigate("/");
  }

  return (
    <>
      <div className={styles.menuButton}>
        <FunctionButton 
          text={"Volver al Menú"}
          onClick={gotoMenu}
          className={styles.menuButton}
        />
      </div>
      <div  className={styles.body}>
        <thead className={styles.text}>
          <tr>
            <th>Nombre</th>
            <th>Mínimo Jugadores</th>
            <th>Máximo Jugadores</th>
            <th>Jugadores Unidos</th>
          </tr>
        </thead>
        {list.map((game, i) => (
          <tbody >
              <tr key={i}>   
                  <td className={styles.name}> 
                  <FunctionButton text={`${game.name}`} onClick={goToForm(game.id)}/>
                  </td>
                  <td>
                      {game.min_players}
                  </td>
                  <td>
                      {game.max_players}
                  </td>
                  <td>
                      {game.amount_of_players}
                  </td>
              </tr>
          </tbody>
        ))}
      </div>
    </>
  );
};

export default GameList;
