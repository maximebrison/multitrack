import { onCleanup, onMount, type Setter } from "solid-js"
import "./uxelements.css"

export type NotifModel = {
    success: boolean
    msg: string
}

function Notification(props: {setter: Setter<NotifModel|null>, success: boolean, msg: string}){
    let timeoutId!: number

    onMount(() => {
        timeoutId = setTimeout(() => props.setter(null), 5000);
    })

    onCleanup(() => {
        clearTimeout(timeoutId);
    })
    return(
        <div class={`notification ${(!props.success) ? "error": ""}`}>
            {props.msg}
        </div>
    )
}

export default Notification;