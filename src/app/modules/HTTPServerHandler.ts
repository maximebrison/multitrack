import express, {type Express, type Request, type Response } from "express";
import { log } from "node:console";
import type { dataFromPlugin, httpServerCallbacks } from "../@types/multitrack.js";

export class HTTPServerHandler{
    app: Express = express();
    port: number = 8030;
    private callbacks!: httpServerCallbacks;

    constructor(port: number){
        this.port = port;

        // Add middlewares
        this.app.use(express.json());

        // Serve static files in ./dist
        this.app.use("/", express.static('dist'));

        // Routes
        this.app.get("/login", (req, res) => {
            res.send("login");
        })

        this.app.post("/data", (req, res) => {
            const data = req.body as dataFromPlugin[];

            res.send(200);
        })

        // SPA Fallback
        this.app.get("/*filepath", (req, res) => {
            res.redirect("/")
        })
    }
        
    public attachCallbacks(callbacks: httpServerCallbacks){
        this.callbacks = callbacks
    }

    run(){
        this.app.listen(this.port, () => {
            log(`App listening on ${this.port}`);
        })
    }
}