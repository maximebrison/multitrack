import { log } from "console";
import type { PluginData, PluginInfo } from "../@types/multitrack.js";
import { wrap } from "../ctx/database.ts";
import { Entity } from "./Entity.ts";

export class Plugin{
    public info: PluginInfo
    public online: boolean = false
    public entities: Entity[] = []

    constructor(info: PluginInfo){
        this.info = info;
    }

    static loadPlugins(){
        wrap((db) => {
            const r = db.prepare("SELECT id, friendly_name, ip_address, port, actions, active FROM plugins WHERE active = 1");
            return r.all()
        })
    }

    public executeAction(action: string, ...args: any[]){

    }

    public updateEntity(data: PluginData){
        const entity = this.entities.find((v, _) => v.serial === data.entity_id);

        if(entity === undefined){
            const newEntity = new Entity(
                this._createEntityDatabaseEntry(data),
                data.entity_id,
                this.info.id
            );

            newEntity.update(data);

            this.entities.push(newEntity)
        } else{
            entity.update(data);
        }
    }

    private _fetchEntitiesFromDatabase(){
        wrap((db) => {
            const entries = db.prepare("SELECT * FROM entities WHERE plugin_id = ? AND hidden = 0").all(this.info.id);
            entries.forEach((v, _) => {
                this.entities.push(new Entity(
                    v["id"]!.valueOf() as number | bigint,
                    v["serial_number"]!.toString(),
                    v["plugin_id"]!.toString()
                ))
            })
        })
    }

    private _createEntityDatabaseEntry(data: PluginData){
        return wrap((db) => {
            const r = db.prepare("INSERT INTO entities(serial_number, friendly_name, plugin_id) VALUES (?, ?, ?)").run(
                data.entity_id,
                data.entity_id,
                this.info.id
            );
            log(`Created entity ${data.entity_id}`);
            return r.lastInsertRowid
        }) as number | bigint
    }
}