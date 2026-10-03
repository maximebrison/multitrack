import { Discoverer } from "./modules/Discoverer.ts";
import { log } from "node:console";
import type { dataFromPlugin, pluginInfo, envelope, signedEnvelope } from "./@types/multitrack.js";
import { WSServerHandler } from "./modules/WSServerHandler.ts";
import { HTTPServerHandler } from "./modules/HTTPServerHandler.ts";

/**
 * Base class for the *Multitrack Core* app.
 */
class MultitrackCore{
    private subscribed: pluginInfo[] = [];
    public discoverer = new Discoverer("multitrack", 5130);
    public ws = new WSServerHandler(8031);
    public http = new HTTPServerHandler(8030);

    public run(){
        this.discoverer.attachCallbacks({
            sendWSMessage: this.send
        })
        this.ws.attachCallbacks({
            onMessageReceived: this.dispatchEnvelopes
        })
        this.http.attachCallbacks({
            onDataReceived: this.dispatchPluginData
        })

        this.http.run();
        this.ws.run();
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
            this.ws.clients.forEach((v, _) => {
                v.send(JSON.stringify(se.envelope))
            })
        } else{
            const client = this.ws.clients.get(se.client_id);

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
    private dispatchEnvelopes = (se: signedEnvelope) => {
        log(`Dispatching envelope to ${se.envelope.dest}`)
        switch(se.envelope.dest){
            case "discoverer":
                this.discoverer.localDispatch(se);
                break;
        }
    }

    /**
     * Dispatches data received from the plugin.
     * 
     * @param data list of radios data in bulk
     */
    private dispatchPluginData = (data: dataFromPlugin[]) => {
        data.forEach((v) => {

        })
    }
}

const app = new MultitrackCore()
app.run()