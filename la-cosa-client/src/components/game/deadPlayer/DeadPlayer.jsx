//create component for dead player
import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./deadPlayer.module.css";
import FunctionButton from "../../functionButton/FunctionButton";

const DeadPlayer = ({socket}) => {
    const navigate = useNavigate();
    const goToHome = () => {
        socket.disconnect();
        navigate("/");
    };

  return (
      <div className={styles.fade}>
        <p className={styles.text}>¡Has sido incinerado! &#128293;</p>
        <FunctionButton text={"Salir de la Partida"} onClick={goToHome}/>
      </div>
  );
};

export default DeadPlayer;