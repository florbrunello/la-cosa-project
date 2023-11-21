import styles from './logs.module.css';
import { useEffect, useState, useRef } from 'react';
import FetchGetLogs from '../../../containers/FetchGetLogs.js';


const Logs = ({socket, gameId}) => {
    const [logs, setLogs] = useState([]);
    const logsDivRef = useRef(null);

    //Function to get logs when it refresh.
    useEffect(() => {
        async function fetchLogs(){
            const resp = await FetchGetLogs({gameId})
            if (resp.status === 200){
                setLogs(resp.json)    
            }
            else{
                console.log("response data: ",resp)
            }
        }
        fetchLogs();
    }, [])

    //Function that recieves a new log and add it to the list of logs
    useEffect(() => {
        socket.on('action',  (data) => setLogs(state => [...state, data]))  
        socket.on('defense', (data) => setLogs(state => [...state, data]))  
        socket.on('discard', (data) => setLogs(state => [...state, data]))
        socket.on("turn_finished", (data) => setLogs(state => [...state, data]));  

        //turns off the listener
        return () => {
            socket.off('action')
            socket.off('defense')
            socket.off('discard')
            socket.off('turn_finished')
        }
    } ,[])


    //Function to scroll down the chat
    useEffect(() => {
        if (logsDivRef.current) {
          logsDivRef.current.scrollTop = logsDivRef.current.scrollHeight;
        }
    }, [logs]);
    
    return (
        <ul className={styles.list} ref={logsDivRef} >
            {logs.map((lg, index) => (
                <div key={index}>
                    <div className={styles.lg}>
                        - {lg.log}
                    </div>
                </div>
            ))}
        </ul>
    )

}

export default Logs; 
