import { useEffect } from "react";
import styles from "./gameAborted.module.css";
import { useNavigate } from "react-router-dom";

const GameAborted = ({socket}) => {
    const navigate = useNavigate();
    useEffect(() => {
        const timeout = setTimeout(() => {
            socket.disconnect();
            navigate("/");            
        }, 3000);

        return () => {
          clearTimeout(timeout);
        };
    }, []);

    return (
        <div className={styles.body}>
            <div className={styles.fade}>
                <p className={styles.text}>El host abandonó la partida.<br />Volviendo al menú principal.<br />&#128557;</p>
            </div>
        </div>
    );
};

export default GameAborted;