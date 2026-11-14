import { onMount, useContext } from "solid-js";
import "./css/maplibre.css";
import { AppContext } from "../ctx/AppContext";

function MapLibre() {
    const ctx = useContext(AppContext)!;

    onMount(() => {
        ctx.map.createMap(ctx.theme.dark);
        ctx.theme.addExtraHandler((dark: boolean) => ctx.map.switchTheme(dark));
    })

    return (
        <>
            <div id="mapRef"></div>
        </>
    )
}

export default MapLibre
