import { createSignal, Show, useContext, type JSXElement, type Setter } from "solid-js"
import StatusLight from "./StatusLight"
import "./topbar.css"
import { ThemeContext } from "../ctx/ThemeContext"

function Topbar(p: {setShowSettings: Setter<boolean>}) {
    const themeController = useContext(ThemeContext);

    return(
        <nav>
            <div class="topbar-left">
                <img src="/favicon.svg" /><h1>Multitrack <i>Core</i></h1>
            </div>
            <div class="topbar-right">
                <button onclick={() => p.setShowSettings(true)}><i class="fa-solid fa-right-from-bracket"></i></button>
                <StatusLight />
                <button onclick={() => themeController?.switchTheme()}><i class="fa-solid fa-circle-half-stroke"></i></button>
                <button onclick={() => p.setShowSettings(true)}><i class="fa-solid fa-wrench"></i></button>
                {/* <form onsubmit={(e) => e.preventDefault()}>
                    <input type="text" placeholder="Send message to server..."></input>
                    <input type="submit" value={"Send"}></input>
                </form> */}
            </div>
        </nav>
    )
}

function QuickAccess(props: {icon: string, children: JSXElement[] | JSXElement}){
    const [show, setShow] = createSignal(false);
    return(
        <div class="topbar-quick-access">
            <button onclick={() => setShow((prev) => !prev)}><i class={props.icon}></i></button>
            <Show when={show()}>
                <div class="topbar-quick-access-dropdown">
                    {props.children}
                </div>
            </Show>
        </div>
    )
}

export default Topbar; QuickAccess