import { For, onMount, useContext } from "solid-js";
import "./css/sidebar.css"
import type { EntityInfo, Envelope } from "../@types/multitrack";
import { createStore } from "solid-js/store";
import { AppContext } from "../ctx/AppContext";

function Sidebar() {
    return(
        <div class="sidebar">
            <Plugin />
        </div>
    )
}

export function Plugin(){
    const ctx = useContext(AppContext)!;
    const [entities, setEntities] = createStore<Record<number,EntityInfo>>();

    onMount(() => {
        ctx.socket.registerMailbox("sidebar", "entity-info", (e: Envelope) => {
            const data = JSON.parse(e.payload!) as EntityInfo
            setEntities(data.serial, data);
            ctx.map.updateMarker(data);
        })
    })
    
    return(
        <div class="sidebar-plugin">
            <h1>Test plugin</h1>
            <For each={Object.values(entities)}>
                {(entity) => <SidebarItem {...entity} />}
            </For>
        </div>
    )
}

function SidebarItem(entity: EntityInfo) {
    const ctx = useContext(AppContext)!;
    return(
        <div 
            class="sidebar-item"
            onClick={() => ctx.map.focus(entity)}
        >
            <div class="sidebar-item-status">
                <span 
                    class={`sidebar-item-status-light fresh`}
                />
            </div>
            <div class="sidebar-item-info">
                <h1>Radio <i>{entity.friendly_name}</i></h1>
                <span>Last status: {entity.last_known_status}</span>
                <span>Last position: {entity.last_known_lat}, {entity.last_known_long}</span>
                <span>Last update: {new Date(entity.last_update).toISOString()}</span>
                <span>Last text: {entity.last_known_text}</span>
            </div>
        </div>
    )
}

export default Sidebar;