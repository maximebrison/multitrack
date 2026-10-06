import { createSignal, Match, Switch, type Setter } from "solid-js";
import "./settings.css"
import Discover from "./SettingsDiscover";

function Settings(p: {setter: Setter<boolean>}){
    const [page, setPage] = createSignal<string>("");

    return(
        <div 
            class="settings-modal"
            onclick={() => p.setter(false)}
        >
            <div 
                class="settings-modal-content"
                onclick={(e) => e.stopPropagation()}    
            >
                <div class="settings-modal-menu">
                    <h1>General</h1>
                    <button onclick={() => setPage("info")}><i class="fa-solid fa-info"></i>Info</button>
                    <h1>Plugins</h1>
                    <button onclick={() => setPage("discover")}><i class="fa-solid fa-tower-broadcast"></i>Discover</button>
                    <button onclick={() => setPage("manage")}><i class="fa-solid fa-list-check"></i>Manage</button>
                </div>
                <div class="settings-modal-page">
                    <Switch fallback={<div>err</div>}>
                        <Match when={page() === "discover"}>
                            <Discover />
                        </Match>
                    </Switch>
                </div>
            </div>
        </div>
    )
}

export default Settings;