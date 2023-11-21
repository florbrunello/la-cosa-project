import { useState } from "react";
import { useForm } from "react-hook-form";
import {valueHasQuotationMarks} from "../../containers/FormValidation.js";
import { FetchJoinGame } from "../../containers/FetchJoinCards.js";
import styles from "./gameJoinForm.module.css";
import FunctionButton from "../functionButton/FunctionButton";
import { useNavigate, useLocation } from "react-router-dom";

const GameJoinForm = () => {
  const navigate = useNavigate();
  const params = useLocation(); 
  const [message, setMessage] = useState("");
  const [errorData, setErrorData] = useState(false);

  let gameId = 0;
  if (!params.state) {
    gameId = 1;
  } else {
    gameId = params.state.gameId;
  }

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      game_id:gameId, 
      player_name: "",
    },
  });

  const onSubmit = async (data) => {
    const response = await FetchJoinGame(data);
    const responseData = {
      playerId: response.json.player_id,
      gameId: response.json.game_id,      
    }
    if (response.status === 200) {
      setErrorData(false);
      navigate(`/game/${responseData.gameId}`, { state: responseData });
    } else if (response.status === 404 || response.status === 422) {
      setMessage(response.json.detail);
      setErrorData(true);
    } else {
      setMessage("Error al unirse a la partida");
      setErrorData(true);
    }
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
      <div className={styles.body}>
        <form>
          {/*Player Name*/}
          <label className={styles.labelJoin} htmlFor="playerName">
            Nombre Jugador
          </label>
          <input
            type="text"
            id="playerName"
            className={styles.inputJoin}
            {...register("player_name", {
              required: {
                value: true,
                message: "Nombre requerido",
              },
              validate: (value) => {
                if (valueHasQuotationMarks(value))
                  return "Nombre del jugador no puede contener comillas";
                else return true;
              },
            })}
          />
          {errors?.player_name && <span className={styles.spanJoin}>{errors.player_name.message}</span>}
          {errorData && <span className={styles.spanJoin}>{message}</span>}

          <div className={styles.buttonJoin}>
              <FunctionButton text={"Unirse"} onClick={handleSubmit(onSubmit)} />
          </div> 
        </form>
      </div>
    </>
  );
};

export default GameJoinForm;
