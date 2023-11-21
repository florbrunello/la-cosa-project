import Player from "../player/Player";
import styles from "./table.module.css";
import Door from "../door/Door"

const Table = ({
    players,
    player,
    playerSelectedState,
    cardSelected,
    discardState,
    turn, 
    obstacles,
    doorSelected, 
    setDoorSelected, 
}) => {
    // sorts players array by table_position in increasing order
    players.sort((a, b) => a.table_position - b.table_position);
    return (
        <div className={styles.container}>
            {players.map((p, index) => {
                return (
                    <>
                    <Player
                        key={index}
                        name={p.name}
                        playerData={players.find((p1) => p1.name === p.name)}
                        player={player}
                        playerSelectedState={playerSelectedState}
                        cardSelected={cardSelected}
                        players={players}
                        setDiscard={discardState.setDiscard}
                        turn={turn}
                        obstacles={obstacles}
                        setDoorSelected={setDoorSelected}
                    />

                    {/* Render the locked door*/}
                    {obstacles.includes(p.table_position) && 
                        <Door doorSelected={doorSelected}
                              setDoorSelected={setDoorSelected}
                              position={p.table_position} 
                              cardSelected={cardSelected} 
                              turn={turn}
                              player={player}
                              players = {players}
                              playerSelectedState={playerSelectedState}
                              discardState={discardState}
                              key={`p${index}`}
                        />} 
                    </>
                )
            })}
        </div>
    );
};


export default Table;