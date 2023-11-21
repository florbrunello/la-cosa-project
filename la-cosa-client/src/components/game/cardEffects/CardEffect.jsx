import { useState, useEffect } from "react";
import React from "react";
import styles from "./cardEffect.module.css"

const CardEffect = ({ showEffect, setShowEffect}) => {
  useEffect(() => {
    const timeout = setTimeout(() => {
      setShowEffect({showEffect: false, data: {}, type: ""});
    }, 3000);

    return () => {
      clearTimeout(timeout);
    };
  }, []);
  console.log("shoeffect",showEffect)

  return (
      <div>
          {/* <p className={styles.text}> {showEffect.data.message} </p> */}
        <div className={styles.cardcontainer}>
          {showEffect.data.cards.map((card, i) => (
            <div className={styles.card} key={i}>
              <img src={`../../src/img/${card.code}${card.number_in_card}.png`}/>
            </div>
          ))}
        </div>
      </div>
  )
}

export default CardEffect;