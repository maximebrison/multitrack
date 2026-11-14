import { useContext, createSignal, onMount, For } from "solid-js";
import "./css/settings-discover.css";
import type { PluginInfo, Envelope } from "../@types/multitrack";
import { AppContext } from "../ctx/AppContext";

function Discover(){
    const ctx = useContext(AppContext)!;
    const [res, setRes] = createSignal<PluginInfo[]>([]);

    onMount(() => {
        ctx.socket.registerMailbox("settings", "discovered-plugins", (e: Envelope) => {            
            if(e.payload){
                let plugin: PluginInfo = JSON.parse(e.payload);
                setRes((prev: PluginInfo[]) => [...prev, plugin]);
            }
        })
    })
    return(
        <div class="settings-plugins-discover">
            <button
                class="settings-plugins-discover-button"
                onclick={() => {
                    setRes([])
                    ctx.socket.send("discoverer", "discover")
                }}
            >
                Discover
            </button>
            <div class="settings-plugins-discover-list">
                <For each={res()}>
                    {(i) => (
                        <Plugin {...i} />
                    )}
                </For>
            </div>
        </div>
    )
}

function Plugin(info: PluginInfo){
    const ctx = useContext(AppContext)!;

    const adopt = async () => {
        const res = await fetch("/admin/adopt", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(info)
        })

        const text = await res.text()

        ctx.utils.notify({
            success: res.ok,
            msg: text
        })
    }

    return(
        <div class="settings-plugins-discover-plugin">
            <div>
                <h1>{`Found on ${info.ip_address}`}</h1>
                <div class="settings-plugins-discover-plugin-infos">
                    <div class="settings-plugins-discover-plugin-line">
                        <div class="key">
                            ID
                        </div>
                        <div class="value">
                            {info.id}
                        </div>
                    </div>
                    <div class="settings-plugins-discover-plugin-line">
                        <div class="key">
                            API Port
                        </div>
                        <div class="value">
                            {info.port}
                        </div>
                    </div>
                    <div class="settings-plugins-discover-plugin-line">
                        <div class="key">
                            Remote actions
                        </div>
                        <div class="value">
                            <For each={info.actions.filter((v) => v.scope === "remote")}>
                                {(a) => (
                                    <span>{`${a.label}`}</span>
                                )}
                            </For>
                        </div>
                    </div>
                    <div class="settings-plugins-discover-plugin-line">
                        <div class="key">
                            Local actions
                        </div>
                        <div class="value">
                            <For each={info.actions.filter((v) => v.scope === "local")}>
                                {(a) => (
                                    <span>{`${a.label}`}</span>
                                )}
                            </For>
                        </div>
                    </div>
                </div>
                <button onclick={() => adopt()}>Claim</button>
            </div>
        </div>
    )
}

export default Discover;