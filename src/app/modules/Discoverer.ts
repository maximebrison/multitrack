import { log } from "node:console"
import { networkInterfaces } from "node:os"
import ip from "ip"
import dgram from "dgram"
import type { discovererCallbacks, pluginInfo, signedEnvelope } from "../@types/multitrack.js"

/**
 * **Discoverer** is used for finding drivers across the subnet of the host running the application.
 * 
 * @param message The message to broadcast. 
 * @param broadcastPort The port to broadcast to. 
 */
export class Discoverer{
    public broadcastPort: number;
    private discovered: pluginInfo[] = [];
    private message: string;
    private callbacks!: discovererCallbacks;

    constructor(message: string, broadcastPort: number){
        this.broadcastPort = broadcastPort;
        this.message = message;
    }

    public attachCallbacks(callbacks: discovererCallbacks){
        this.callbacks = callbacks
    }

    public localDispatch(se: signedEnvelope){
        switch(se.envelope.action){
            case "discover":
                this.discover(se.client_id);
                break;
        }
    }

    public discover(clientId: string){
        const broadcastIP = this.getLocalBroadcastIP();
        const socket = dgram.createSocket("udp4");

        log("Discovering")

        socket.on('listening', () => {
            socket.setBroadcast(true);
            socket.send(this.message, this.broadcastPort, broadcastIP);
        })

        socket.on('message', (msg, rinfo) => {
            log(`Received ${msg.toString()} from ${rinfo.address}`)
            const se: signedEnvelope = {
                client_id: clientId,
                envelope: {
                    dest: "settings-drivers",
                    action: "respond",
                    payload: msg.toString()
                }
            }

            this.callbacks.sendWSMessage(se)
        })

        socket.bind(0);
    }

    private getLocalBroadcastIP(){
        const localIP = ip.address();
        const ifaces = networkInterfaces();
        var mask: string = "";

        for(var i in ifaces){
            var iface = ifaces[i]

            iface?.forEach((v) => {
                if (v.address === localIP){
                    mask = v.netmask
                    return
                }
            })

            if(mask !== undefined) break;
        }

        return ip.subnet(localIP, mask).broadcastAddress
    }
}