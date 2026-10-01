import { createSignal, onMount, useContext } from "solid-js";
import "./mainframe.css"
import MapLibre from "./MapLibre"
import Sidebar from "./Sidebar";
import { SocketContext } from "../ctx/SocketContext";

function Mainframe() {
    const socketController = useContext(SocketContext);
    const [online, setOnline] = createSignal(socketController?.status);

    onMount(() => {
        socketController?.subscribeIndicator(setOnline);
    })

    return(
        <div class={`mainframe ${(online()) ? "online" : "offline"}`}>
            <MapLibre />
            <Sidebar />
        </div>
    )
}

export default Mainframe;