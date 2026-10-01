import { Discoverer } from "./Discoverer.ts";
import { log } from "node:console";
import type { driver, envelope, signedEnvelope } from "./@types/multitrack.js";
import { WSServerHandler } from "./WSServerHandler.ts";

/**
 * Base class for the *Multitrack Core* app.
 */
class MultitrackCore{
    private subscribed: driver[] = [];
    public discoverer = new Discoverer("multitrack", 5130);
    public wsserver = new WSServerHandler(8031);

    public run(){
        this.discoverer.attachCallbacks({
            sendWSMessage: this.send
        })
        this.wsserver.attachCallbacks({
            onMessageReceived: this.dispatch
        })

        this.wsserver.run()
    }

    /**
     * Sends the **envelope** based on the *clientID*.
     * 
     * If the *clientID* is set to **everyone**, the *envelope* is broadcast across all connected clients.
     *
     * @param se **signedEnvelope**, containing the **clientId** plus the actual **envelope**.
     */
    private send = (se: signedEnvelope) => {
        if(se.client_id === "everyone"){
            this.wsserver.clients.forEach((v, _) => {
                v.send(JSON.stringify(se.envelope))
            })
        } else{
            const client = this.wsserver.clients.get(se.client_id);

            if(client !== undefined){
                client.send(JSON.stringify(se.envelope));
            }
        }
    }

    /**
     * Dispatches received **signedEnvelope** to the right local dispatcher, based on the **dest** prop.
     * 
     * @param se **signedEnvelope**, containing the clientId plus the actual **envelope**.
     */
    private dispatch = (se: signedEnvelope) => {
        log(`Dispatching envelope to ${se.envelope.dest}`)
        switch(se.envelope.dest){
            case "discoverer":
                this.discoverer.localDispatch(se);
                break;
        }
    }
}

const app = new MultitrackCore()
app.run()