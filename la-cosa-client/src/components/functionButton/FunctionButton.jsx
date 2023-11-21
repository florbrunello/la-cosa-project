import style from './functionButton.module.css'

const FunctionButton = ({
    text,
    onClick
}) => {
    return (
    <div className={style.container} >
        <button className={style.button24} onClick={onClick}>{text}</button>
    </div>
    )
}

export default FunctionButton;