import express, {type Express, type Request, type Response } from "express";
import { log } from "node:console";

export class HTTPServerHandler{
    app: Express = express();
    port: number = 8030;

    constructor(port: number){
        this.port = port;

        // Serving static files in ./dist
        this.app.use("/", express.static('dist'));

        // Routes
        this.app.get("/login", (req, res) => {
            res.send("login");
        })

        // SPA Fallback
        this.app.get("/*filepath", (req, res) => {
            res.redirect("/")
        })

        log(this.app.get('env'));
    }

    run(){
        this.app.listen(this.port, () => {
            log(`App listening on ${this.port}`);
        })
    }
}