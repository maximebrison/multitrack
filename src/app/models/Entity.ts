import { error, log } from "console"
import type { PluginData, TextMessage, GPSPosition, StatusUpdate } from "../@types/multitrack.js"
import { wrap } from "../ctx/database.ts"

export class Entity{
    id: number | bigint
    serial: string
    pluginId: string
    friendlyName: string
    hidden: boolean = false
    lastUpdate: number
    lastKnownLat: number | undefined
    lastKnownLong: number | undefined
    lastKnownStatus: string | undefined
    lastKnownText: string | undefined

    constructor(id: number | bigint, serial: string, pluginId: string){
        this.id = id;
        this.serial = serial;
        this.pluginId = pluginId;
        this.friendlyName = serial;
        this.lastUpdate = new Date().getUTCDate();
    }

    /**
     * Updates the data in RAM and pushes changes to the Database.
     * 
     * @param data 
     */
    public update(data: PluginData){
        if(data.success){
            switch (data.type){
                case "text":
                    let text = data.data as TextMessage;
                    this.lastUpdate = data.timestamp;
                    this.lastKnownText = text.msg;
                    wrap((db) => {
                        try{
                            db.prepare("INSERT INTO text_messages(entity_id, timestamp, direction, text) VALUES (?, ?, ?, ?)").run(
                                this.id,
                                data.timestamp,
                                0,
                                text.msg
                            );
                        } catch(e){
                            error(e);
                        }
                    })
                    break;
                case "gps":
                    let gps = data.data as GPSPosition;
                    this.lastUpdate = data.timestamp;
                    this.lastKnownLat = gps.latitude;
                    this.lastKnownLong = gps.longitude;
                    wrap((db) => {
                        try{
                            db.prepare("INSERT INTO positions(entity_id, timestamp, lat, long) VALUES (?, ?, ?, ?)").run(
                                this.id,
                                data.timestamp,
                                gps.latitude,
                                gps.longitude
                            );
                        } catch(e){
                            error(e);
                        }
                    })
                    break;
                case "status":
                    let status = data.data as StatusUpdate;
                    this.lastKnownStatus = status.status;
                    wrap((db) => {
                        try{
                            db.prepare("INSERT INTO statuses(entity_id, timestamp, status) VALUES (?, ?, ?)").run(
                                this.id,
                                data.timestamp,
                                status.status,
                            );
                        } catch(e){
                            error(e);
                        }
                    })
                    break;
                default:
                    log("Invalid type");
            }
        }
    }
}