import { useContext, useMemo, useState, useEffect } from "react";
import styles from "./player.module.css";

const Player = ({
  name,
  playerData,
  player,
  playerSelectedState,
  cardSelected,
  players,
  setDiscard,
  turn, 
  obstacles, 
  setDoorSelected
}) => {
  const turnOwner = turn.owner;
  const turnState = turn.state; 
  const playersAlive = players.filter((player) => player.alive);

  const isAlive = useMemo(() => playerData ? playerData.alive : undefined, [playerData]);
  const hasTurn = useMemo(() => turnOwner === playerData.table_position, [playerData, turnOwner]);
  const hasQuarantine = useMemo (() => playerData ? playerData.quarantine !== 0 : undefined, [playerData]);
  const [playersToSelect, setPlayersToSelect] = useState([]);
  let turnOwnerIndex; 
  
  const playerStyle = playerSelectedState.name === name ? styles.playerSelected : styles.playerStyle;

  const style = {
    backgroundColor: (isAlive && hasQuarantine) ? "rgb(200, 40, 40)" : (isAlive ? (playerSelectedState.name === name ? "rgb(100, 240, 250)" : "rgb(70, 190, 119)") : "rgb(100, 100, 100)"),    
    borderColor: hasTurn ? "rgb(255, 127, 80)" : (playerSelectedState.name === name ? "rgb(250, 250, 250)" : "rgb(0, 0, 0)"),
  };

  useEffect(() => {
    if (cardSelected.cardId == undefined) {
      playerSelectedState.setPlayerSelected({});
    }
  },[cardSelected])

  
  const getAdyacentPlayersWithNoLockedDoor = (player_on_left, player_on_right) => {
    
    //check if some of the adyacent players has locked door
    if (obstacles.includes(player.table_position) && 
        obstacles.includes(player_on_left.table_position)){
      return [];
    }
    else if (obstacles.includes(player.table_position)){
      return [player_on_left]
    }
    else if (obstacles.includes(player_on_left.table_position))
      return [player_on_right];
    else 
      return [player_on_left, player_on_right]; 
  } 

  useEffect(() => {
    // obtain the player alives next to the turnOwner
    turnOwnerIndex = playersAlive.findIndex(player => player.table_position === turnOwner);  
    const player_on_right = playersAlive[(turnOwnerIndex + 1) % playersAlive.length];
    const player_on_left = playersAlive[(((turnOwnerIndex - 1) + playersAlive.length) % playersAlive.length)];  
    const player_three_on_right = playersAlive[(turnOwnerIndex + 3) % playersAlive.length];
    const player_three_on_left = playersAlive[(((turnOwnerIndex - 3) + playersAlive.length) % playersAlive.length)];  

    const pTS = () => {    
      switch (cardSelected.code){
        //sospecha, análisis, lanzallamas, cambio de lugar
        case "sos": //sospecha
        case "ana": //análisis
        case "ptr": //puerta atrancada
        case "qen": //Que quede entre nosotros
        case "cua": //cuarentena
          return getAdyacentPlayersWithNoLockedDoor(player_on_left, player_on_right) 
        case "lla": //lanzallamas
          if (player.quarantine == 0){
            return getAdyacentPlayersWithNoLockedDoor(player_on_left, player_on_right)        
          }
          else {
            return [];
          }

        case "sed": //seducción
        case "sda": //sal de aquí
        case "npa": //¿no podemos ser amigos?
          const allAlivePlayers = playersAlive.filter(player => player.table_position != turnOwner && player.quarantine == 0);

          //check if some of the adyacent players has locked door
          if (obstacles.includes(player.table_position) && 
              obstacles.includes(player_on_left.table_position)){

            return allAlivePlayers.filter(player => player.table_position !== player_on_right.table_position && 
                                                    player.table_position !== player_on_left.table_position);
          }
          else if (obstacles.includes(player.table_position)){
            return allAlivePlayers.filter(player => player.table_position !== player_on_right.table_position);
          }
          else if (obstacles.includes(player_on_left.table_position))
            return allAlivePlayers.filter(player => player.table_position !== player_on_left.table_position);
          else 
            return allAlivePlayers

        case "cdl": //cambio de lugar           
          if (player.quarantine == 0){
            // if (player_on_right.quarantine == 0 && player_on_left.quarantine == 0)
            //   return [player_on_left, player_on_right];        
            // else if (player_on_right.quarantine !== 0)
            //   return [player_on_left];
            // else if (player_on_left.quarantine !== 0)
            //   return [player_on_right]

              return getAdyacentPlayersWithNoLockedDoor(player_on_left, player_on_right).filter(player => player.quarantine == 0)
          }
          else {
            return [];
          }
        case "mvc": //más vale que corras
          if (player.quarantine == 0){
            return playersAlive.filter(player => player.table_position != turnOwner && player.quarantine == 0);
          }
          else {
            return [];
          }
        
        case "hac": //hacha 
          //gets the adyacent players in quarantine.
          const adyacentPlayers = [player_on_left, player_on_right].filter(player => player.quarantine !== 0);

          if (player.quarantine !== 0){
            adyacentPlayers.push(player);
          }
          console.log("adyacentPlayers", adyacentPlayers);
          return adyacentPlayers;

        case "und": //uno, dos ...
          return [player_three_on_left, player_three_on_right].filter(player => player.quarantine == 0);

        default: // defense cards, wiskey, vigila tus espaldas and other panic cards
          return [];
      }
    };
    setPlayersToSelect(pTS());

    if(playerSelectedState.name !== playersToSelect.filter(player => player.name === playerSelectedState.name).name){
      playerSelectedState.setPlayerSelected({});
    }

    
  }, [cardSelected]);


    
  const selectPlayer = () => {
    if (name === playerSelectedState.name){
      playerSelectedState.setPlayerSelected({});
    }
    else if ( cardSelected.cardId !== undefined &&
              turnState === 1){
        //if a card has been selected. 
        /*check how to select depending on the card selected 
        if the card is sospecha or cambio de lugar => select adyacent player
        if the card is whisky, vigila tus espaldas or ups => don't select player
        if the card is mas vale que corras => select any player who is alive */
      switch (cardSelected.code){
        case "sos": //sospecha
        case "ana": //análisis
        case "lla": //lanzallamas
        case "cdl": //cambio de lugar
        case "mvc": //mas vale que corras
        case "sed": //seducción
        case "sda": //sal de aquí 
        case "cua": //cuarentena
        case "ptr": //puerta atrancada 
        case "hac": //hacha
        case "qen": //queda entre nosotros
        case "npa": //¿no podemos ser amigos?
        case "und": //uno, dos ...
          if (playersToSelect.filter(player => player.name === name).length !== 0){
            playerSelectedState.setPlayerSelected({ name: name });
            setDiscard(false);
            setDoorSelected(0);
          }
          break; 
        default: // defense cards, wiskey and vigila tus espaldas
          playerSelectedState.setPlayerSelected({});
          setDiscard(false);
          setDoorSelected(0);
        }
  };} 
  

  return (
    <div className={playerStyle} style={style} onClick={selectPlayer} data-testid={"player-"+name}>
      {name === player.name ? <span className={styles.me}>{"Tu"}</span> : <span className={styles.playerText}>{playerData.name}</span>}
    </div>
  )
}

export default Player;
