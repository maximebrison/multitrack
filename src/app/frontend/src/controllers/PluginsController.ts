import type { PluginInfo } from "../@types/multitrack";

export class PluginsController{
    plugins: PluginInfo[] = []

    public loadPlugins(plugins: PluginInfo[]){
        this.plugins = plugins;
    }
}