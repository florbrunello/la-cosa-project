import styles from './chat.module.css';
import { useEffect, useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { valueHasQuotationMarks } from "../../../containers/FormValidation.js";
import FetchSendMessage from '../../../containers/FetchSendMessage';
import FetchGetChat from '../../../containers/FetchGetChat';


const Chat = ({socket, gameId, playerName}) => {
    const [messages, setMessages] = useState([]);
    const chatDivRef = useRef(null);

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors },
      } = useForm({
        defaultValues: {
          content: " ",
          sender: playerName,
        },
    });

    //Function to get chat when it refresh.
    useEffect(() => {
        async function fetchChat(){
            const resp = await FetchGetChat({gameId})
            if (resp.status === 200){
                setMessages(resp.json)
            }
            else{
                console.log("response data: ",resp)
            }
        }
        fetchChat();
    }, [])

    //Function that recieves the new message and add it to the list of messages
    useEffect(() => {
        socket.on('new_message', (data) => setMessages(state => [...state, data]))  

        //turns off the listener
        return () => {
            socket.off('new_message')
        }
    } ,[])


    //Fuction to send message
    const onSubmit = async (data) => {
        reset();
        const response = await FetchSendMessage({gameId,data})
        if(response.code === 200){
            console.log("mensaje enviado")
        }
        else{
            console.log("response", response)
        }
    } 

    //Function to scroll down the chat
    useEffect(() => {
        if (chatDivRef.current) {
          chatDivRef.current.scrollTop = chatDivRef.current.scrollHeight;
        }
    }, [messages]);
    
    return (
        <div className={styles.body} >
          
            {/*List of messages*/}
            <ul className={styles.list} ref={chatDivRef} >
                {messages.map((message, index) => (
                <div className={message.sender === playerName ? styles.msgRight : styles.msg}
                    key={index}>
                        <div>
                            <span className={styles.sender}>{message.sender}</span>: {message.content}
                        </div>
                    </div>
                ))}
            </ul>

            {/*Message input*/}
            <form className={styles.input}>
                <input
                type="text"
                id="msg"
                data-testid="input"
                className={styles.inputCreation}
                {...register("content", {
                    required: {
                    value: true,
                    message: "Mensaje requerido",
                    },
                    validate: (value) => {
                    if (valueHasQuotationMarks(value))
                        return "No puede contener comillas";
                    else if (/^\s+$/.test(value))
                        return "Debe contener letras o números";
                    else return true;
                    },
                })}
                />
                <button className={styles.button} onClick={handleSubmit(onSubmit)}>Enviar</button>
                
            </form>
                {errors?.content && (
                <span className={styles.spanInput}>
                    {errors.content.message}
                </span>
                )}

           

        </div>
    )

}

export default Chat; 
