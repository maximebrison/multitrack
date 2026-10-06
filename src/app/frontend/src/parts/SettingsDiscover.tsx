import { SocketContext } from "../ctx/SocketContext";
import { UtilitiesContext } from "../ctx/UtilitiesContext";
import { useContext, createSignal, onMount, For } from "solid-js";
import "./settingsdiscover.css";
import type { pluginInfo, envelope } from "../@types/multitrack";

function Discover(){
    const utilitiesController = useContext(UtilitiesContext);
    const socketController = useContext(SocketContext);
    const [res, setRes] = createSignal<pluginInfo[]>([]);

    onMount(() => {
        socketController?.registerMailbox('settings-plugins', (e: envelope) => {
            console.log(e.payload);
            
            if(e.payload){
                let plugin: pluginInfo = JSON.parse(e.payload);
                setRes((prev: pluginInfo[]) => [...prev, plugin]);
            }
        })
    })
    return(
        <div class="settings-plugins-discover">
            <button
                onclick={() => {
                    socketController?.send("discoverer", "discover")
                }}
            >
                Discover
            </button>
            <div>
                <For each={res()}>
                    {(i) => (
                        <div class="settings-plugins-item">
                            <h1>{`Found "${i.id}"`}</h1>
                            <h2>{`${i.ip_address}:${i.port}`}</h2>
                            <span>{`Actions : ${i.actions}`}</span>
                            <span>{(i.text) ? "Supports text" : "Doesn't support text"}</span>
                            <button onclick={() => utilitiesController?.notify({success: true, msg: "test"})}>Adopt</button>
                        </div>
                    )}
                </For>
            </div>
        </div>
    )
}

export default Discover;