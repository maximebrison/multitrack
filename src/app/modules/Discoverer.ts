import { error, log } from "node:console"
import { networkInterfaces } from "node:os"
import dgram from "dgram"
import type { DiscovererCallbacks, PluginInfo, SignedEnvelope } from "../@types/multitrack.js"

/**
 * **Discoverer** is used for finding plugins across the *Core's network*.
 * 
 * @param message The message to broadcast. 
 * @param broadcastPort The port to broadcast to. 
 */
export class Discoverer{
    public discoveryPort: number;
    public multicastGroup: string;
    public multicastInterface: string;
    public message: string;
    private _callbacks!: DiscovererCallbacks;

    constructor(message: string, discoveryPort: number, multicastGroup: string = "239.255.42.69", multicastInterface: string = "auto"){
        this.discoveryPort = discoveryPort;
        this.multicastGroup = multicastGroup;
        this.multicastInterface = multicastInterface;
        this.message = message;
    }

    /**
     * Attach **callbacks** from the Core. Is used to handle *child-to-parent* methods sharing.
     * 
     * @param callbacks 
     */
    public attachCallbacks(callbacks: DiscovererCallbacks){
        this._callbacks = callbacks
    }

    /**
     * Dispatches **SignedEnvelopes** to local methods.
     * 
     * @param se 
     */
    public localDispatch(se: SignedEnvelope){
        switch(se.envelope.action){
            case "discover":
                this.discover(se.client_id);
                break;
        }
    }

    /**
     * Sends the *discovery message* to the network.
     * 
     * @param clientId Used to know which *Websocket client* made the request, therefore sending the response to the right one.
     * @param timeout Sets how long *(in miliseconds)* the socket should listen for responses.
     */
    public discover(clientId: string, timeout = 2000){
        const seen = new Set<string>();
        const sockets: dgram.Socket[] = [];

        // Opens a socket on every non-internal interface found by _getLocalIpv4Addresses().
        for(const ifaceIP of this._getLocalIPv4Addresses()){
            const socket = dgram.createSocket("udp4");
            sockets.push(socket);

            socket.on("error", (e) => {
                error(`Discovery error on ${ifaceIP}: ${e.message}`)
                socket.close()
            })

            socket.on("listening", () => {
                socket.setMulticastInterface(ifaceIP);
                socket.send(this.message, this.discoveryPort, this.multicastGroup);
            })

            socket.on("message", (msg, rinfo) => {
                try{
                    const info: PluginInfo = JSON.parse(msg.toString());
                    if(seen.has(info.id)) return;
                    seen.add(info.id);
                    info.ip_address = rinfo.address;

                    const se: SignedEnvelope = {
                        client_id: clientId,
                        envelope: {
                            dest: "settings",
                            action: "discovered-plugins",
                            payload: JSON.stringify(info)
                        }
                    }

                    this._callbacks.sendWSMessage(se)
                    log(`Received info from ${info.id}`)
                } catch(e){
                    error(`Error while unpacking info from ${rinfo.address}. Received \n${msg.toString()}`)
                }
            })

            socket.bind(0, ifaceIP)
        }

        // Closes the sockets after X seconds, defined by the 'timeout' parameter.
        setTimeout(() => {
            sockets.forEach((s) => {
                try{
                    s.close();
                } catch{}
            })
        }, timeout)
    }

    /**
     * Fetches *non-internal* **IPv4 addresses** on all of the machine's interfaces. 
     * 
     * @returns A list of IPv4 addresses (string[])
     */
    private _getLocalIPv4Addresses(){
        const ifaces = networkInterfaces();
        const addrs: string[] = []

        for(const iface of Object.values(ifaces)){
            if(iface){
                iface.forEach((v, _) => {
                    if(!v.internal && v.family === "IPv4"){
                        addrs.push(v.address);
                    }
                })
            } else{
                log("No interface found.")
            }
        }

        return addrs;
    }
}