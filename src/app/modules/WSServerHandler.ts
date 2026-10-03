import { log } from "console"
import { WebSocketServer, type WebSocket } from "ws"
import type { envelope, signedEnvelope, wsServerCallbacks } from "../@types/multitrack.d.ts"
import { v4 as uuid4 } from "uuid";

export class WSServerHandler{
    public port: number;
    public clients: Map<string, WebSocket> = new Map<string, WebSocket>();
    private callbacks!: wsServerCallbacks;

    constructor(port: number){
        this.port = port;
    }
    
    public attachCallbacks(callbacks: wsServerCallbacks){
        this.callbacks = callbacks
    }

    public run(){
        const wss = new WebSocketServer({
            port: this.port
        })

        wss.on('connection', (ws) => {
            const clientId = uuid4()
            this.clients.set(clientId, ws)

            log("Core connected")

            const handler = (data: {client_id: string, dest: string, action: string, payload: string}) => {
                if(data.client_id !== clientId) return;
                const e: envelope = {
                    dest: data.dest,
                    action: data.action,
                    payload: data.payload
                }
                ws.send(JSON.stringify(e));
            }

            ws.on('message', (m) => {
                try{
                    const e = JSON.parse(m.toString()) as envelope;
                    this.callbacks.onMessageReceived({client_id: clientId, envelope: e});
                } catch(e){
                    log(`Error ${e} receiving this message ${m.toString()}`)
                }
            })

            ws.on('close', () => {
                this.clients.delete(clientId);
            })
        })
    }

    public send(se: signedEnvelope){
        const client = this.clients.get(se.client_id);
        if(client === undefined){
            log(`Client ${se.client_id} not found, message not sent.`)
            return
        }

        client.send(JSON.stringify(se.envelope));
    }
}