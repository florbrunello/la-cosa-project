import { useState } from "react";
import { set, useForm } from "react-hook-form";
import { valueHasQuotationMarks } from "../../containers/FormValidation.js";
import styles from "./gameCreationForm.module.css";
import FunctionButton from "../functionButton/FunctionButton";
import { useNavigate } from "react-router-dom";
import { FetchCreateGame } from "../../containers/FetchGameCreate.js";

const GameCreationForm = () => {
  const navigate = useNavigate();
  const [errorData, setErrorData] = useState(false);
  const [message, setMessage] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      game: { name: "", min_players: 4, max_players: 12 },
      host: { name: "" },
    },
  });

  const onSubmit = async (data) => {
    const response = await FetchCreateGame(data);
    const responseData = {
      gameId: response.json.game_id,
      playerId: response.json.player_id,
    };
    if (response.status === 201) {
      setErrorData(false);
      navigate(`/game/${response.json.game_id}`, { state: responseData });
    } else {
      setMessage(response.json.detail);
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
        <form className={styles.creationForm}>
          {/*Host Name*/}
          <label className={styles.labelCreation} htmlFor="hostName">
            &nbsp; &nbsp;Nombre Host
          </label>
          <input
            type="text"
            id="hostName"
            className={styles.inputCreation}
            {...register("host.name", {
              required: {
                value: true,
                message: "Nombre requerido",
              },
              validate: (value) => {
                if (valueHasQuotationMarks(value))
                  return "No puede contener comillas";
                else return true;
              },
            })}
          />
          {errors?.host?.name && (
            <span className={styles.spanCreation}>
              {errors.host.name.message}
            </span>
          )}

          {/*Game Name*/}
          <label className={styles.labelCreation} htmlFor="gameName">
            Nombre Partida
          </label>
          <input
            type="text"
            id="gameName"
            className={styles.inputCreation}
            {...register("game.name", {
              required: {
                value: true,
                message: "Campo requerido",
              },
              validate: (value) => {
                if (valueHasQuotationMarks(value))
                  return "Partida no puede contener comillas";
                else return true;
              },
            })}
          />
          {errors?.game?.name && (
            <span className={styles.spanCreation}>
              {errors.game.name.message}
            </span>
          )}

        {/*Min Players*/}
        <label className={styles.labelCreation} htmlFor="minPlayers">
              Mínimo Jugadores
              </label>
              <input
                type="number"
                id="minPlayers"
                className={styles.inputCreation}
                {...register("game.min_players", {
                  required: {
                    value: true,
                    message: "Ingrese valor numérico",
                  },
                  validate: (value) => {
                  if ( value < 4 || value > 12)
                      return "Ingrese valor entre 4 y 12";
                    else return true;
                  },
                })}
              />
              {errors?.game?.min_players && (
                <span className={styles.spanCreation}>
                  {errors.game.min_players.message}
                </span>
              )}

        {/*Max Players*/}
      <label className={styles.labelCreation} htmlFor="maxPlayers">
              Máximo Jugadores
              </label>
              <input
                type="number"
                id="maxPlayers"
                className={styles.inputCreation}
                {...register("game.max_players", {
                  required: {
                    value: true,
                    message: "Ingrese valor numérico",
                  },
                  validate: (value) => {
                    if ( value < 4 || value > 12)
                      return "Ingrese valor entre 4 y 12";
                    else return true;
                  },
                })}
              />
              {errors?.game?.max_players && (
                <span className={styles.spanCreation}>
                  {errors.game.max_players.message}
                </span>
              )}

          {errorData && (
            <span className={styles.spanCreation} role="alert">
              {message}
            </span>
          )}

          <div className={styles.button}>
            <FunctionButton
              text={"Crear Partida"}
              onClick={handleSubmit(onSubmit)}
            />
          </div>
        </form>
      </div>
    </>
  );
};

export default GameCreationForm;
