import { createSignal, onMount, Show, useContext } from "solid-js";
import "./css/app.css"
import Topbar from "./parts/Topbar";
import Mainframe from "./parts/Mainframe";
import Settings from "./parts/Settings";
import type { NotifModel } from "./parts/UXElements";
import Notification from "./parts/UXElements";
import { UtilitiesContext } from "./ctx/UtilitiesContext";


function App() {
    const [showSettings, setShowSettings] = createSignal(false);
    const [notif, setNotif] = createSignal<NotifModel|null>(null);
    const utilitiesController = useContext(UtilitiesContext);

    onMount(() => {
        utilitiesController?.init(setNotif);
    })

    return (
        <div class="app">
            <Topbar setShowSettings={setShowSettings}/>
            <Mainframe />
            <Show when={showSettings()}>
                <Settings setter={setShowSettings}/>
            </Show>
            <Show when={notif()}>
                <Notification setter={setNotif} {...notif()!} />
            </Show>
        </div>
    )
}

export default App
