import { log } from "node:console";
import { DatabaseSync } from "node:sqlite";

const DB_PATH = "data/test.db";
const CREATE_PLUGINS = `
    CREATE TABLE "plugins" (
        "id" text,
        "friendly_name" text NOT NULL,
        "ip_address" text NOT NULL,
        "port" integer NOT NULL,
        "actions" text NOT NULL,
        "token_hash" text NOT NULL,
        "active" integer NOT NULL,
        PRIMARY KEY ("id")
    );
`
const CREATE_ENTITIES = `
    CREATE TABLE "entities" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "serial_number" text NOT NULL,
        "friendly_name" text NOT NULL,
        "plugin_id" text NOT NULL,
        "hidden" integer NOT NULL,
        CONSTRAINT fk_plugins_entities
        FOREIGN KEY (plugin_id)
        REFERENCES plugins(id)
    );
`
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
    );
`
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
    );
`
const CREATE_STATUSES = `
    CREATE TABLE "statuses" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "entity_id" integer NOT NULL,
        "timestamp" real NOT NULL,
        "status" text NOT NULL
    );
`

/**
 * Checks if the database exists (checks the entities table). Creates it if not.
 */
function init(){
    wrap((db) => {
        if (db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='entities';").get() === undefined){
            log("Creating database...");
            db.exec(CREATE_PLUGINS);
            db.exec(CREATE_ENTITIES);
            db.exec(CREATE_TEXT_MESSAGES);
            db.exec(CREATE_POSITIONS);
            db.exec(CREATE_STATUSES);
            log("Done.");
        }
    });
}

/**
 * Wraps SQL Queries with a Database opening and closing statement.
 * 
 * @param fn SQL Queries handler.
 * @returns Whatever the *fn* returns.
 */
function wrap(fn: (db: DatabaseSync) => any){
    const db = new DatabaseSync(DB_PATH);
    const r = fn(db);
    db.close();
    return r
}

export { init, wrap };