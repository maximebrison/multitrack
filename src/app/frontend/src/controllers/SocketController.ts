import { type Setter } from "solid-js";
import type { Envelope } from "../@types/multitrack";

export class SocketController{
    public status: boolean = false
    public socket: WebSocket | undefined
    private mailboxes: Map<string, Map<string, Function>> = new Map();
    private indicators: Setter<boolean>[] = []

    /**
     * Connects to the *Core's WebSocket Server*. Notify its *status* on the OnlineIndicator.tsx
     */
    public run(){
        this.socket = new WebSocket("ws://192.168.1.21:8030/clients");

        this.socket.onopen = () => {
            this.changeStatus(true)
        }

        this.socket.onclose = () => {
            this.changeStatus(false)
        }

        this.socket.onmessage = (e) => {
            console.log(e.data);
            this.dispatch(JSON.parse(e.data));
        }
    }

    /**
     * Wraps *parameters* in an **Envelope** before sending to the *Core*.
     * 
     * @param dest 
     * @param action 
     * @param payload 
     */
    public send(dest: string, action: string, payload: string | null = null){
        const e: Envelope = {
            dest: dest,
            action: action,
            payload: payload
        }

        this.socket!.send(JSON.stringify(e));
    }

    /**
     * Dispatches received *Envelope* to the right **id/action** combo (mailbox).
     * 
     * @param e 
     * @returns 
     */
    public dispatch(e: Envelope){
        console.log(`Dispatching to ${e.dest}`);
        
        const mb = this.mailboxes.get(e.dest);
        if(!mb){
            console.log(`No mailbox named ${e.dest}`);
            return            
        }

        mb.get(e.action)!(e)

        console.log("Dispatched");
    }

    /**
     * Registers **handler** to the right **id/action** combo (mailbox).
     * 
     * @param id 
     * @param action 
     * @param handler 
     */
    public registerMailbox(id: string, action: string, handler: Function){
        const mb = this.mailboxes.get(id);
        if(mb){
            mb.set(action, handler)
        } else{
            this.mailboxes.set(
                id,
                new Map<string, Function>().set(action, handler)
            )
        }
    }

    /**
     * Changes the *up* status, and reccursively calls additional *indicator handlers*.
     * 
     * @param status 
     */
    public changeStatus(status: boolean){
        this.status = status;
        this.indicators.forEach((fn) => fn(this.status))
    }

    /**
     * Appends *setter* to the list of handlers called when the *status* changes.
     * 
     * @param setter 
     */
    public subscribeIndicator(setter: Setter<boolean>){
        if(!this.indicators.includes(setter)){
            this.indicators.push(setter);
        }
    }
}

// class Mailbox{
//     id: string
//     action: string
//     handler: Function

//     constructor(id: string, action: string, handler: Function){
//         this.id = id;
//         this.action = action;
//         this.handler = handler;
//     }
// }