import { createSignal, For, onMount, useContext, type Setter } from "solid-js";
import "./settings.css"
import { SocketContext } from "../ctx/SocketContext";
import type { envelope } from "../controllers/SocketController";
import { UtilitiesContext } from "../ctx/UtilitiesContext";

type driver = {
    id: string,
    name: string,
    ws_port: string,
    radio_type: string
}

function Settings(p: {setter: Setter<boolean>}){
    const socketController = useContext(SocketContext);
    const utilitiesController = useContext(UtilitiesContext);
    const [res, setRes] = createSignal<string[]>([]);

    onMount(() => {
        socketController?.registerMailbox('settings-drivers', (e: envelope) => {
            console.log(e.payload);
            
            if(e.payload){
                let driver = e.payload
                setRes((prev: string[]) => [...prev, driver]);
            }
        })
    })

    return(
        <div 
            class="settings-modal"
            onclick={() => p.setter(false)}
        >
            <div 
                class="settings-modal-content"
                onclick={(e) => e.stopPropagation()}    
            >
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
                            <div>
                                <span>{i}</span><button onclick={() => utilitiesController?.notify({success: true, msg: "test"})}>Adopt</button>
                            </div>
                        )}
                    </For>
                </div>
            </div>
        </div>
    )
}

export default Settings;