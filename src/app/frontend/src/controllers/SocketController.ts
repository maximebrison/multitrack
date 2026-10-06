import { type Setter } from "solid-js";
import type { envelope } from "../@types/multitrack";

export class SocketController{
    public status: boolean = false
    public socket: WebSocket | undefined
    private mailboxes = new Map<string, Function>();
    private indicators: Setter<boolean|undefined>[] = []

    public run(){
        this.socket = new WebSocket("ws://192.168.1.21:8031");

        this.socket.onopen = () => {
            this.changeStatus(true)
        }

        this.socket.onclose = () => {
            this.changeStatus(false)
        }

        this.socket.onmessage = (e) => {
            this.dispatch(JSON.parse(e.data));
        }
    }

    public send(dest: string, action: string, payload: string | null = null){
        const e: envelope = {
            dest: dest,
            action: action,
            payload: payload
        }

        this.socket!.send(JSON.stringify(e));
    }

    public dispatch(e: envelope){
        console.log(`Dispatching to ${e.dest}`);
        
        const handler = this.mailboxes.get(e.dest);
        if(handler === undefined){
            console.log(`No mailbox named ${e.dest}`);
            return            
        }

        handler(e)

        console.log("Dispatched");
    }

    public registerMailbox(id: string, handler: Function){
        this.mailboxes.set(id, handler);
    }

    public changeStatus(status: boolean){
        this.status = status;
        this.indicators.forEach((fn) => fn(this.status))
    }

    public subscribeIndicator(setter: Setter<boolean|undefined>){
        if(!this.indicators.includes(setter)){
            this.indicators.push(setter);
        }
    }
}