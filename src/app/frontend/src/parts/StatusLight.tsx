import { createSignal, onMount, useContext } from "solid-js";
import "./css/status-light.css"
import { AppContext } from "../ctx/AppContext";

function StatusLight() {
    const ctx = useContext(AppContext)!;
    const [online, setOnline] = createSignal(ctx.socket.status);
    
    onMount(() => {
        ctx.socket.subscribeIndicator(setOnline);
    })

    return(
        <div onclick={() => ctx.socket.run()} class={`online-indicator ${(online()) ? "online" : "offline"}`}><div class="led"></div>{(online()) ? "ONLINE" : "OFFLINE"}</div>
    )
}

export default StatusLight;