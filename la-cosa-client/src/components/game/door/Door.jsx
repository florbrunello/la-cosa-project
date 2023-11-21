
import imgSrc from "../../../img/door.png"
import { useEffect, useState } from "react";
import styles from "./door.module.css";

const Door = ({
    doorSelected, 
    setDoorSelected,
    position,
    cardSelected, 
    turn, 
    player, 
    players, 
    playerSelectedState,
    discardState
}) => {

    const [stylesDoor, setStylesDoor] = useState(styles.door);

    useEffect(()=> {
        if (playerSelectedState.name !== undefined || discardState.discard ){
            setDoorSelected(0);
            setStylesDoor(styles.door);
        }
    }, [playerSelectedState.name, discardState.discard])
       
    const selectDoor = () => {
        //If there was a door selected and another door is clicked => deselect previous door and select new door

        if (doorSelected === position &&  turn.owner == player.table_position){
            setDoorSelected(0);
            setStylesDoor(styles.door);
        }
        else if (turn.owner == player.table_position  && turn.state == 1 ){ 
            
            if (position === player.table_position ||
                (player.table_position === 1 ? (position === players.length) : (position === player.table_position - 1))
                ){ 
                    switch(cardSelected.code){
                        case "hac":
                            setDoorSelected(position);
                            playerSelectedState.setPlayerSelected({});
                            setStylesDoor(styles.doorSelected);
                            discardState.setDiscard(false);
                            break; 
                        default:
                            setDoorSelected(0);
                            setStylesDoor(styles.door);
                    }
                }
        }
        else {
            setDoorSelected(0);
            setStylesDoor(styles.door);
        }
    }

    return (
        <div onClick={() => selectDoor()} className={stylesDoor} >
            <img src={imgSrc}></img>
        </div>
    );
};


export default Door;