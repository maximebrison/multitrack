import { Discoverer } from "./modules/Discoverer.ts";
import { log } from "node:console";
import type { PluginData, Envelope, SignedEnvelope, TextMessage, GPSPosition, StatusUpdate, PluginInfo } from "./@types/multitrack.js";
import { MultitrackServer } from "./modules/MultitrackServer.ts";
import { Plugin } from "./models/Plugin.ts";

/**
 * Base class for the *Multitrack Core* app.
 */
class MultitrackCore{
    public discoverer = new Discoverer("multitrack", 5130);
    public server = new MultitrackServer(8030);
    public entities: Entity[] = [];

    public run(){
        this.discoverer.attachCallbacks({
            sendWSMessage: this.sendToClient
        })
        this.server.attachCallbacks({
            onMessageReceived: this.dispatchEnvelopes,
            onDataReceived: this.dispatchPluginData,
        })

        Plugin.loadPlugins();
        this.server.run();
    }

     /**
     * Dispatches **SignedEnvelopes** to local methods.
     * 
     * @param se 
     */
    public localDispatch(se: SignedEnvelope){
        
    }

    /**
     * Sends the **Envelope** based on the *clientID*.
     * 
     * If the *clientID* is set to **everyone**, the *Envelope* is broadcast across all connected clients.
     *
     * @param se **SignedEnvelope**, containing the **clientId** plus the actual **Envelope**.
     */
    private sendToClient = (se: SignedEnvelope) => {
        if(se.client_id === "everyone"){
            this.server.clients.forEach((v, _) => {
                v.send(JSON.stringify(se.envelope))
            })
        } else{
            const client = this.server.clients.get(se.client_id);

            if(client !== undefined){
                client.send(JSON.stringify(se.envelope));
            }
        }
    }

    /**
     * Dispatches received **SignedEnvelope** to the right local dispatcher, based on the **dest** prop.
     * 
     * @param se **SignedEnvelope**, containing the clientId plus the actual **Envelope**.
     */
    private dispatchEnvelopes = (se: SignedEnvelope) => {
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
     * @param data list of entities data in bulk
     */
    private dispatchPluginData = (data: PluginData) => {
        // If entity doesn't already exists, creates a new one.
        let entity = this.entities.find((v, _) => v.plugin_id === data.plugin_id && v.serial === data.entity_id);
        if(!entity){
            entity = new Entity(data.entity_id, data.plugin_id);
            this.entities.push(entity);
        }

        entity.update(data);

        this.sendToClient({
            client_id: "everyone",
            envelope: {
                dest: "sidebar",
                action: "entity-info",
                payload: JSON.stringify(entity)
            }
        })
    }
}

class Entity{
    serial: string
    plugin_id: string
    friendly_name: string
    last_update: number
    last_known_lat: number | undefined
    last_known_long: number | undefined
    last_known_status: string | undefined
    last_known_text: string | undefined

    constructor(serial: string, plugin_id: string){
        this.serial = serial;
        this.plugin_id = plugin_id;
        this.friendly_name = serial.toString();
        this.last_update = new Date().getUTCDate();
    }

    /**
     * Updates the data in RAM.
     * 
     * @param data 
     */
    public update(data: PluginData){
        if(data.success){
            switch (data.type){
                case "text":
                    let text = data.data as TextMessage;
                    this.last_update = data.timestamp;
                    this.last_known_text = text.msg;
                    break;
                case "gps":
                    let gps = data.data as GPSPosition;
                    this.last_update = data.timestamp;
                    this.last_known_lat = gps.latitude;
                    this.last_known_long = gps.longitude;
                    break;
                case "status":
                    let status = data.data as StatusUpdate;
                    this.last_known_status = status.status;
                    break;
                default:
                    log("Invalid type");
            }
        }
    }
}

const app = new MultitrackCore()
app.run()