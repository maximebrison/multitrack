import express, { type Express } from "express";
import { error, log } from "node:console";
import type { Envelope, MultitrackServerCallbacks, PluginData, PluginInfo } from "../@types/multitrack.js";
import { createServer } from "node:http";
import { WebSocketServer, type WebSocket } from "ws";
import { v4 as uuid4 } from "uuid";
import session from "express-session";
import { randomBytes } from "node:crypto";
import { sha256 } from "js-sha256";
import { Authenticator } from "./Authenticator.ts";
import { Database } from "./Database.ts";
import { init } from "../ctx/database.ts";

/**
 * Manages the **HTTP server** (http, express) and the two **WebSocket Servers** (ws).
 * 
 * All three share the same port (default: `8030`), and the `http.createServer()` handles the **WebSocket upgrade**
 */
export class MultitrackServer{
    public clients: Map<string, WebSocket> = new Map();
    public plugins: Map<string, WebSocket> = new Map();
    public authenticator = new Authenticator();
    public db = new Database();
    private _callbacks!: MultitrackServerCallbacks;
    private _port: number = 8030;

    constructor(port: number){
        this._port = port;
        // Loads plugins tokens from the DB to RAM.
        init();
        this.authenticator.loadPluginTokens(this.db.getPluginsTokens())
    }

    /**
     * Attach **callbacks** from the Core. Is used to handle *child-to-parent* methods sharing.
     * 
     * @param callbacks 
     */
    public attachCallbacks(callbacks: MultitrackServerCallbacks){
        this._callbacks = callbacks;
    }
    
    /**
     * Runs the **HTTP Server** *(for serving static files)*, the **Client WebSocket Server** *(that handles client-server communication)* 
     * and the **Plugins WebSocket Server** *(to gather info from the plugins)*.
     */
    public run(){
        const app = express();
        const server = createServer(app);
        const wss_client = new WebSocketServer({ noServer: true });
        const wss_plugins = new WebSocketServer({ noServer: true });

        // Handles the Client WebSocket connection.
        wss_client.on('connection', (ws) => {
            const clientId = uuid4();
            this.clients.set(clientId, ws);

            log("Core connected");

            ws.on('message', (data) => {
                try{
                    const e = JSON.parse(data.toString()) as Envelope;
                    this._callbacks.onMessageReceived({client_id: clientId, envelope: e});
                } catch(e){
                    log(`Error ${e} receiving this message ${data.toString()}`);
                }
            })

            ws.on('close', () => {
                this.clients.delete(clientId);
            })
        })

        // Handles the Plugins WebSocket connection.
        wss_plugins.on('connection', (ws) => {
            log("Plugin connected");

            ws.on('message', (data) => {
                try{
                    const pluginData = JSON.parse(data.toString()) as PluginData;
                    this._processPluginData(pluginData);
                } catch(e){
                    error(`Something went wrong when processing PluginData: ${e}`);
                }
            })

            ws.on('close', () => {
                log("Plugin disconnected")
            })
        })

        // Routes the WebSocket Upgrade to the right handler. 
        server.on("upgrade", (req, sock, head) => {
            const url = new URL(req.url!, `ws://localhost`);

            switch(url.pathname){
                case "/clients":
                    wss_client.handleUpgrade(req, sock, head, (ws) => {
                        wss_client.emit("connection", ws, req);
                    })
                    break;
                case "/plugins":
                    if(this.authenticator.authorizePlugin(url, req)){
                        wss_plugins.handleUpgrade(req, sock, head, (ws) => {
                            wss_plugins.emit("connection", ws, req);
                        })
                    } else{
                        sock.write("HTTP/1.1 401 Unauthorized\r\n\r\n");
                        sock.destroy();
                    }
                    break;
                default:
                    sock.write("HTTP/1.1 404 Not Found\r\n\r\n");
                    sock.destroy();
            }
        })

        // Handles the Express server.
        // Add middlewares
        app.use(express.json());
        app.use(session({
            secret: "abc123",
            resave: false,
            saveUninitialized: true
        }))

        // Serve static files in ./dist
        app.use("/", express.static('dist'));

        // Routes
        this._initRoutes(app);

        server.listen(this._port, () => {
            log(`Listening on ${this._port}`);
        })
    }

    private _processPluginData(data: PluginData){
        if(data.success){
            switch(data.type){
                case "gps":
                    this.db.createPosition(data);
                    break;
                case "status":
                    this.db.createStatus(data);
                    break;
                case "text":
                    this.db.createMessageFromPlugin(data);
                    break;
                case "err":
                    error(`Received "err" from ${data.plugin_id}`)
                    break;
                default:
                    throw new Error(`Received unexpected data from ${data.plugin_id}`)
            }

            this._callbacks.onDataReceived(data);
        }
    }

    private _initRoutes(app: Express){
        // Initialize routers
        const adminRouter = express.Router();
        adminRouter.use((req, res, next) => {
            if(!req.session.user) next()
            else res.status(401).send("Unauthorized")
        })

        // Auth
        app.post("/login", (req, res) => {
            log("Logging in...");
            req.session.user = "user";
            res.send("Logged in.");
        })

        app.get("/test", (req, res) => {
            res.send("This is a test");
        }) 

        app.get("/adopted_plugins", (req, res) => {
            res.send(this.db.getPlugins());
        }) 

        // Plugins
        adminRouter.post("/adopt", async (req, res) => {
            try{
                // Gather PluginInfo from the request body and generates a random base64 token.
                const info: PluginInfo = req.body;
                const token = randomBytes(32).toString("base64url");
                // Sends the generated token to the right ip:port, then awaits the response.
                const response = await fetch(`${req.protocol}://${info.ip_address}:${info.port}/adopt`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        host: req.host,
                        token: token
                    })
                })
                // If status == 200, the plugin was free and now is bound to this Core.
                if(response.status === 200){
                    this.authenticator.loadPluginTokens(this.db.getPluginsTokens().set(info.id, sha256(token)));
                    this.db.createPlugin(info, token);
                } 

                const text = await response.text();
                res.status(response.status).send(text);
            } catch(e){
                log(`Couldn't adopt plugin: ${e}`);
            }
        })

        // SPA Fallback
        app.get("/*filepath", (req, res) => {
            res.redirect("/");
        })

        app.use("/admin", adminRouter);
    }
}