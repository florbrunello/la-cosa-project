import { useState, useEffect} from "react";
import style from "./game.module.css";
import Hand from "./hand/Hand";
import Table from "./table/Table";
import Deck from "./deck/Deck";
import FetchPlayCard from "../../containers/FetchPlayCard";
import DeadPlayer from "./deadPlayer/DeadPlayer";
import FetchDiscard from "../../containers/FetchDiscard";
import FetchResponse from "../../containers/FetchResponse";
import FetchEndTurn from "../../containers/FetchEndTurn";
import DeclareVictory from "../../containers/DeclareVictory";
import ExchangeCard from "../../containers/ExchangeCard";
import ResponseExchange from "../../containers/ResponseExchange";
import Chat from "./chat/Chat";
import Logs from "./logs/Logs";
import CardEffect from "./cardEffects/CardEffect";
import ActionButtons from "./actionButtons/ActionButtons";
import Instruction from "./instruction/Instruction";

const Game = ({ socket, player, gameData, gameId, playerId }) => {
  const [cardSelected, setCardSelected] = useState({}); //{cardId, code, kind}
  const [playerSelected, setPlayerSelected] = useState({}); //{name}
  const [canPlayCard, setCanPlayCard] = useState(false);
  const [discard, setDiscard] = useState(false);
  const [hasCardToDefendExchange, setHasCardToDefendExchange] = useState(false);
  const [actionText, setActionText] = useState("");
  const [hasCardToDefend, setHasCardToDefend] = useState(false);  
  const [showEffect, setShowEffect] = useState({showEffect: false, data: {}, type: ""});
  const [cardLifted, setCardLifted] = useState(false);
  const [instructionReciever, setInstructionReciever] = useState("")
  const [doorSelected, setDoorSelected] = useState(0);
  const [playedCard, setPlayedCard] = useState({});
  const [cardsSelected, setCardsSelected] = useState([]);

  socket.on("analisis", (data) => setShowEffect({showEffect: true, data, type: "analisis"}));
  socket.on("whisky", (data) => setShowEffect({showEffect: true, data, type: "whisky"}));
  socket.on("sospecha", (data) => setShowEffect({showEffect: true, data, type: "sospecha"}));
  socket.on("quarantine", (data) => setShowEffect({showEffect: true, data, type: "quarantine"}));
  socket.on("ups", (data) => setShowEffect({showEffect: true, data, type: "ups"}));
  socket.on("ate", (data) => setShowEffect({showEffect: true, data, type: "aterrador"}));
  socket.on("qen", (data) => setShowEffect({showEffect: true, data, type: "aterrador"}));

  const players = gameData.players;
  const turn = gameData.turn;
  const turnState = turn.state; 

  useEffect(() => {
    if (turnState === 5 && player.table_position === turn.owner)  {
      FetchEndTurn({
        gameId
      });
    }
  }, [turn]);

  useEffect(() => {
    switch(turnState) {
      // making decision
      case 1:
        const action = discard ? "discard" : "playCard";
        if (discard && cardSelected !== undefined) {
          setActionText("Descartar carta");
        } else {
          setActionText("Jugar carta");
        }
        switch (cardSelected.code) {
          case "whk":
          case "vte":
          case "det":
          case "cpo":
          case "trc":
          case "ups":
          case "eaf":
          case "cac":
          case "olv":
            setCanPlayCard({
              canPlayCard: (playerSelected.name === undefined || discard) &&
                            cardSelected.cardId !== undefined,
              action: action,
            });
            break;

          case "hac": 
            setCanPlayCard({
              canPlayCard: (( playerSelected.name !== undefined || discard ) ||  (doorSelected !== 0 ) )&&
                            cardSelected.cardId !== undefined,
              action: action,
            });
            break;
          default:
            setCanPlayCard({
              canPlayCard:
                (playerSelected.name !== undefined || discard) &&
                cardSelected.cardId !== undefined,
              action: action,
            });
            break;
        }
        break;
      
      // exchange beginning
      case 3:
        setInstructionReciever(players.filter((player) => player.table_position === turn.owner)[0].name);
        setCanPlayCard({
          canExchangeCard: (cardSelected.cardId !== undefined)
        });
        setActionText("Intercambiar carta");
        break;
      case 4:
        setInstructionReciever(turn.destination_player_exchange);
        setCanPlayCard({
          canExchangeCard: (cardSelected.cardId !== undefined)
        });

        setHasCardToDefendExchange(cardSelected.code === "fal" || 
                                   cardSelected.code === "ate" ||
                                   cardSelected.code === "ngs" );

        
        setActionText("Intercambiar carta");
        break;
      case 6:
        switch (playedCard.code){
          case "cac":
            setActionText("Intercambiar carta con el mazo");
            setCanPlayCard({
              canPlayCard: (cardsSelected.length === 1),
              action: "panic"
            });
            break;
          case "olv":
            setActionText("Intercambiar cartas con el mazo");
            setCanPlayCard({
              canPlayCard: (cardsSelected.length === 3),
              action: "panic"
            });
            break;
        }
        break;
      default: 
        break;
    }
  }, [playerSelected, discard, cardSelected, turn, doorSelected, cardsSelected]);

  const playCard = () => {
    if (canPlayCard.action === "discard") { //check if the action is discard
      FetchDiscard({
        gameId: gameId,
        playerId: playerId,
        cardId: cardSelected.cardId,
      });
    } else if (canPlayCard.action === "playCard") {//check if the action is play card
      FetchPlayCard({
        gameId: gameId,
        playerId: playerId,
        cardId: cardSelected.cardId,
        destinationName:
          playerSelected.name === undefined ? player.name : playerSelected.name,
        obstacleType: (cardSelected.code === "hac" ? (doorSelected !== 0 ? "ptr" : "cua"): null),
        obstaclePosition: doorSelected !== 0 ? doorSelected : null,
      });
    } else if (canPlayCard.action === "panic") {
      switch(playedCard.code){
        case "cac":
          socket.emit(playedCard.code, {
            game_id: gameId,
            player_id: playerId,
            panic_card_id: playedCard.cardId,
            card_id: cardsSelected[0]
          })
          break;
        case "olv":
          socket.emit(playedCard.code, {
            game_id: gameId,
            player_id: playerId,
            panic_card_id: playedCard.cardId,
            card_id: cardsSelected
          })
          break;
      }
    }

    setPlayedCard(cardSelected);
    setPlayerSelected({});
    setCardSelected({});
    setDiscard(false);
    setDoorSelected(0);
  };

  const defendCard = (cardToDefend) => {
    if (cardToDefend !== null) {
      setHasCardToDefend(true);
    } else {
      defend(false);
    }
  };

  const defend = (defend) => {
    FetchResponse({
      gameId: gameId,
      playerId: playerId,
      responseCardId: defend ? cardSelected.cardId : null,
    });
    setHasCardToDefend(false);
    setCardSelected({});
  };

  const exchangeCard = (defend) => {
    if(turnState === 3){
      ExchangeCard({
        gameId: gameId,
        playerId: playerId,
        cardId: cardSelected.cardId
      })
    } else if (turnState === 4){
      ResponseExchange({
        gameId: gameId,
        playerId: playerId,
        cardId:        defend ? null : cardSelected.cardId,
        defenseCardId: defend ? cardSelected.cardId : null 
      })
    }
    setCardSelected({});
  }

  return (
    <>
      <div className={style.general} data-testid="game">
          <div className={style.topbox} >
              <div className={style.instruction}>
                {player.name === instructionReciever ? (
                  <Instruction  state={turnState} 
                                cardLifted={cardLifted}
                                cardSelected={cardSelected}
                  />
                ) : (
                  <span>Espera tu turno para ser parte de la acción!</span>
                )
                }
              </div>        
              <div className={style.table}>
                <Table  players={players} 
                        player={player}
                        playerSelectedState={{name: playerSelected.name, setPlayerSelected}}
                        cardSelected={cardSelected}
                        discardState={{discard, setDiscard}}
                        turn={gameData.turn}
                        obstacles={gameData.obstacles}
                        doorSelected={doorSelected}
                        setDoorSelected={setDoorSelected}
                        />
              </div>        
          </div>
          <div className={style.bottombox} >
              <div className={style.buttonsLogsContainer} >
                  <div className={style.buttons}>
                    <ActionButtons  DeclareVictory={DeclareVictory} 
                                    defend={defend}
                                    playCard={playCard}
                                    exchangeCard={exchangeCard}
                                    player={player}
                                    playerId={playerId}
                                    gameId={gameId}
                                    hasCardToDefend={hasCardToDefend}
                                    canPlayCard={canPlayCard}
                                    hasCardToDefendExchange={hasCardToDefendExchange}
                                    actionText={actionText}
                    />
                  </div>        
                  <div className={style.logs}>
                    <Logs socket={socket} gameId={gameId} />
                  </div>        
              </div>
              <div className={style.deckHandContainer} >
                  <div className={style.deck}>
                    {showEffect.showEffect ? (
                      <CardEffect showEffect={showEffect} setShowEffect={setShowEffect}/>
                    ) : (
                      <Deck player={player} 
                            playDirection={gameData.play_direction} 
                            gameId={gameId}
                            turnOwner={turn.owner}
                            turnState={turnState}
                            cardSelected={cardSelected}
                            discardState={{discard, setDiscard}}
                            setPlayerSelected={setPlayerSelected}
                            setCardLifted={setCardLifted}
                            setInstructionReciever={setInstructionReciever}
                      />
                    )}
                  </div>        
                  <div className={style.hand}>
                    {player.alive ? (
                      <Hand
                        player={player}
                        turn={turn}
                        setCardSelected={setCardSelected}
                        defendCard={defendCard}
                        cardSelected={cardSelected}
                        cardsSelectedStatus={{cardsSelected, setCardsSelected, playedCard}}
                      />
                    ) : (
                      <DeadPlayer socket={socket} />
                    )}
                  </div>        
              </div>
              <div className={style.chatContainer}>
                <Chat socket={socket} gameId={gameId} playerName={player.name} />
              </div>
          </div>

      </div>        
    </>
  )
};

export default Game;
