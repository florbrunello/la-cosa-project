import { useNavigate } from "react-router-dom"
import FunctionButton from "../functionButton/FunctionButton"
import style from "./Home.module.css"

const Home = () => {
    const navigate = useNavigate()
    const gotoCreateGame = () => {
        navigate("/game-creation-form")
    }

    const gotoListGame = () => {
        navigate("/list-games")
    }

    return (
        <div className={style.home}>
            <title>La Cosa</title>
            <h1>La Cosa</h1>
            <FunctionButton text={"Crear Partida"} onClick={gotoCreateGame}/>
            <FunctionButton text={"Unirse a Partida"} onClick={gotoListGame}/>
        </div>
    )
}

export default Home;