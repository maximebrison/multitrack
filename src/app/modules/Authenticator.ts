import type { IncomingMessage } from "node:http";
import { sha256 } from "js-sha256";
import { log } from "node:console";

export class Authenticator{
    public pluginTokens: Map<string, string> = new Map();

    /**
     * 
     * @param tokens Map<plugin_id, token_hash>
     */
    public loadPluginTokens(tokens: Map<string, string>){
        this.pluginTokens = tokens;
    }

    /**
     * Fetches the **id** from the *url searchParams*, the **bearer-token** header from the *IncomingMessage*
     * then see if it checks out from *self.pluginTokens* (loaded from the Database at startup).
     * 
     * @param url URL
     * @param req IncomingMessage
     * @returns `true` if the check was successful, `false` otherwise
     */
    public authorizePlugin(url: URL, req: IncomingMessage): boolean {
        const id = url.searchParams.get("id");
        const token = req.headers["bearer-token"] as string | undefined;

        log(`${id}, ${token}`)

        if(id && token && this.pluginTokens.get(id) === sha256(token)){
            return true;
        }

        return false;
    }
}