import { error, log } from "node:console";
import { DatabaseSync } from "node:sqlite";
import type { ActionModel, GPSPosition, PluginData, PluginInfo, StatusUpdate, TextMessage } from "../@types/multitrack.js";
import { sha256 } from "js-sha256";

/**
 * Handles **Database creation** and **CRUD** operations.
 */
export class Database{
    public dbPath = "data/test.db";

    /**
     * Wraps SQL Queries with a Database opening and closing statement.
     * 
     * @param fn SQL Queries handler.
     * @returns Whatever the *fn* returns.
     */
    public wrap(fn: (db: DatabaseSync) => any){
        const db = new DatabaseSync(this.dbPath);
        const r = fn(db);
        db.close();
        return r
    }

    public createPlugin(plugin: PluginInfo, token: string){
        this.wrap((db) => {
            const plugin_query = db.prepare("INSERT INTO plugins (id, friendly_name, ip_address, port, actions, token_hash, active) VALUES (?, ?, ?, ?, ?, ?, ?)");
            plugin_query.run(
                plugin.id, 
                plugin.id, 
                plugin.ip_address, 
                plugin.port, 
                JSON.stringify(plugin.actions),
                sha256(token),
                1
            );
        })
    }

    public getPluginsTokens(){
        return this.wrap((db) => {
            const tokens = new Map<string, string>()
            const q = db.prepare("SELECT id, token_hash FROM plugins");
            q.all().forEach((v, _) => {
                if(v["id"] && v["token_hash"]){
                    tokens.set(v["id"].toString(), v["token_hash"].toString())
                }
            })
            return tokens
        }) as Map<string, string>
    }

    public createPosition(data: PluginData){
        this.wrap((db) => {
            try{
                const id = this._getEntityId(data.entity_id, data.plugin_id);
                const positionData = data.data as GPSPosition;
                db.prepare("INSERT INTO positions(entity_id, timestamp, lat, long) VALUES (?, ?, ?, ?)").run(
                    id,
                    data.timestamp,
                    positionData.latitude,
                    positionData.longitude
                );
            } catch(e){
                error(e);
            }
        })
    }

    public createStatus(data: PluginData){
        this.wrap((db) => {
            try{
                const id = this._getEntityId(data.entity_id, data.plugin_id);
                const statusData = data.data as StatusUpdate;
                db.prepare("INSERT INTO statuses(entity_id, timestamp, status) VALUES (?, ?, ?)").run(
                    id,
                    data.timestamp,
                    statusData.status,
                );
            } catch(e){
                error(e);
            }
        })
    }

    public createMessageFromPlugin(data: PluginData){
        this.wrap((db) => {
            try{
                const id = this._getEntityId(data.entity_id, data.plugin_id);
                const textData = data.data as TextMessage;
                db.prepare("INSERT INTO text_messages(entity_id, timestamp, direction, text) VALUES (?, ?, ?, ?)").run(
                    id,
                    data.timestamp,
                    0,
                    textData.msg
                );
            } catch(e){
                error(e);
            }
        })
    }

    public getPlugins(){
        return this.wrap((db) => {
            type PluginFromDb = {
                id: string,
                friendly_name: string,
                actions: ActionModel
            }
            const plugins: PluginFromDb[] = []
            const res = db.prepare("SELECT id, friendly_name, actions FROM plugins").all();
            
            res.forEach((v, _) => {
                plugins.push({
                    id: v["id"]!.toString(),
                    friendly_name: v["friendly_name"]!.toString(),
                    actions: JSON.parse(v["actions"]!.toString())
                })
            })

            return plugins;
        })
    }

    private _getEntityId(entityId: string, pluginId: string){
        return this.wrap((db) => {
            const res = db.prepare("SELECT id FROM entities WHERE serial_number = ? AND plugin_id = ?").get(entityId, pluginId);
            if(res === undefined){
                const r = db.prepare("INSERT INTO entities(serial_number, friendly_name, plugin_id, hidden) VALUES (?, ?, ?, ?)").run(
                    entityId,
                    entityId,
                    pluginId,
                    0
                );
                log(`Created entity ${entityId}`);
                return r.lastInsertRowid
            } else{
                return res["id"] as number | bigint
            }
        }) as number | bigint
    }
}

const CREATE_PLUGINS = `
CREATE TABLE "plugins" (
    "id" text,
    "friendly_name" text NOT NULL,
    "ip_address" text NOT NULL,
    "port" integer NOT NULL,
    "actions" text NOT NULL,
    "token_hash" text NOT NULL,
    PRIMARY KEY ("id")
);`

const CREATE_ENTITIES = `
CREATE TABLE "entities" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"serial_number" text NOT NULL,
	"friendly_name" text NOT NULL,
	"plugin_id" text NOT NULL,
	CONSTRAINT fk_plugins_entities
    FOREIGN KEY (plugin_id)
    REFERENCES plugins(id)
);`

const CREATE_TEXT_MESSAGES = `
CREATE TABLE "text_messages" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "entity_id" integer NOT NULL,
    "timestamp" real NOT NULL,
    "direction" integer NOT NULL,
    "text" text NOT NULL,
    CONSTRAINT fk_entities_messages
    FOREIGN KEY (entity_id)
    REFERENCES entities(id)
);`

const CREATE_POSITIONS = `
CREATE TABLE "positions" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "entity_id" integer NOT NULL,
    "timestamp" real NOT NULL,
    "lat" real NOT NULL,
    "long" real NOT NULL,
    CONSTRAINT fk_entities_positions
    FOREIGN KEY (entity_id)
    REFERENCES entities(id)
);`

const CREATE_STATUSES = `
CREATE TABLE "statuses" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "entity_id" integer NOT NULL,
    "timestamp" real NOT NULL,
    "status" text NOT NULL
);`