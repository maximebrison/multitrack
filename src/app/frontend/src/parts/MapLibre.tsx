import { Map, Marker, NavigationControl, Popup, addProtocol, setWorkerUrl } from "maplibre-gl"
import 'maplibre-gl/dist/maplibre-gl.css';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import { Protocol } from "pmtiles"
import { onMount, useContext } from "solid-js"
import { layers, namedFlavor } from "@protomaps/basemaps";
import { ThemeContext } from "../ctx/ThemeContext";
import "./maplibre.css"

function MapLibre() {
    const themeController = useContext(ThemeContext);

    let map!: Map;

    let protocol = new Protocol();
    addProtocol("pmtiles", protocol.tile);
    setWorkerUrl(workerUrl)

    onMount(() => {
        map = new Map({
            container: "mapRef",
            center: [4.87, 50.47], // [lon, lat]
            zoom: 10,
            style: {
                version: 8,
                glyphs: location.origin + "/fonts/{fontstack}/{range}.pbf",
                sprite: location.origin + `/sprites/v4/${(themeController?.dark) ? "dark" : "light"}`,
                sources: {
                protomaps: {
                    type: "vector",
                    url: "pmtiles://"+location.origin+"/belgium.pmtiles",
                    attribution: "© <a href='https://openstreetmap.org'>OpenStreetMap</a> contributors",
                },
                },
                layers: layers("protomaps", namedFlavor((themeController?.dark) ? "dark" : "light"), { lang: "fr" }),
            },
        });

        const scale = new NavigationControl();
        map.addControl(scale);

        const popup = new Popup({offset: 25})
            .setHTML(`
                <h1>Radio ABC123Z</h1><br />
                <i>Last seen at Long. 4.959351978617836, Lat. 50.40292135661877</i><br />
                <a href='http://crouton.net'>link</a>
            `)

        new Marker()
            .setLngLat([4.959351978617836, 50.40292135661877])
            .setPopup(popup)
            .addTo(map)

        themeController?.addExtraHandler(themeHandler);
    })

    const addLocation = () => {
        const popup = new Popup({offset: 25})
            .setHTML(`
                <h1>Radio ABC123Z</h1><br />
                <i>Last seen at Long. 4.959351978617836, Lat. 50.40292135661877</i><br />
                <a href='http://crouton.net'>link</a>
            `)

        new Marker()
            .setLngLat([4.959351978617836, 50.40292135661877])
            .setPopup(popup)
            .addTo(map)

        console.log("Added location");
    }

    const themeHandler = () => {
        map.setStyle(null); // To ease the reloading of the map, it flickers otherwise

        map.setStyle({
            version: 8,
            glyphs: location.origin + "/fonts/{fontstack}/{range}.pbf",
            sprite: location.origin + `/sprites/v4/${(themeController?.dark) ? "dark" : "light"}`,
            sources: {
                protomaps: {
                    type: "vector",
                    url: "pmtiles://"+location.origin+"/belgium.pmtiles",
                    attribution: "© <a href='https://openstreetmap.org'>OpenStreetMap</a> contributors",
                },
            },
            layers: layers("protomaps", namedFlavor((themeController?.dark) ? "dark" : "light"), { lang: "fr" }),
        })
    }

    return (
        <>
            <div id="mapRef"></div>
        </>
    )
}

export default MapLibre
