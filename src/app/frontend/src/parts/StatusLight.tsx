import { createSignal, onMount, useContext } from "solid-js";
import { SocketContext } from "../ctx/SocketContext";
import "./statuslight.css"

function StatusLight() {
    const socketController = useContext(SocketContext);
    const [online, setOnline] = createSignal(socketController?.status);
    
    onMount(() => {
        socketController?.subscribeIndicator(setOnline);
    })

    return(
        <div onclick={() => socketController?.run()} class={`status-light ${(online()) ? "online" : "offline"}`}><div class="led"></div>{(online()) ? "ONLINE" : "OFFLINE"}</div>
    )
}

export default StatusLight;