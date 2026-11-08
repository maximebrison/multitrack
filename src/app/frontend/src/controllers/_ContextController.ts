import { MapController } from "./MapController";
import { PluginsController } from "./PluginsController";
import { SocketController } from "./SocketController";
import { ThemeController } from "./ThemeController";
import { UtilitiesController } from "./UtilitiesController";

export class ContextController{
    map = new MapController();
    socket = new SocketController();
    theme = new ThemeController();
    utils = new UtilitiesController();
    plugins = new PluginsController();
}