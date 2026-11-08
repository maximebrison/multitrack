import { Marker, Popup, Map as Maplibre, NavigationControl, addProtocol, setWorkerUrl } from "maplibre-gl";
import 'maplibre-gl/dist/maplibre-gl.css';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import type { EntityInfo } from "../@types/multitrack";
import { layers, namedFlavor } from "@protomaps/basemaps";
import { Protocol } from "pmtiles";

export class MapController{
    public map!: Maplibre;
    public markers: Map<number,Marker> = new Map();

    public createMap(dark: boolean){
        let protocol = new Protocol();
        addProtocol("pmtiles", protocol.tile);
        setWorkerUrl(workerUrl)
        
        this.map = new Maplibre({
            container: "mapRef",
            center: [4.87, 50.47],
            zoom: 10,
            style: {
                version: 8,
                glyphs: location.origin + "/fonts/{fontstack}/{range}.pbf",
                sprite: location.origin + `/sprites/v4/${(dark) ? "dark" : "light"}`,
                sources: {
                protomaps: {
                    type: "vector",
                    url: "pmtiles://"+location.origin+"/map.pmtiles",
                    attribution: "<a href='https://protomaps.com/'>Protomaps</a> © <a href='https://openstreetmap.org'>OpenStreetMap</a> contributors",
                },
                },
                layers: layers("protomaps", namedFlavor((dark) ? "dark" : "light"), { lang: "fr" }),
            },
        });

        const scale = new NavigationControl();
        this.map.addControl(scale);
    }

    public switchTheme(dark: boolean){
        this.map.setStyle(null); // To ease the reloading of the map, it flickers otherwise

        this.map.setStyle({
            version: 8,
            glyphs: location.origin + "/fonts/{fontstack}/{range}.pbf",
            sprite: location.origin + `/sprites/v4/${(dark) ? "dark" : "light"}`,
            sources: {
                protomaps: {
                    type: "vector",
                    url: "pmtiles://"+location.origin+"/map.pmtiles",
                    attribution: "<a href='https://protomaps.com/'>Protomaps</a> © <a href='https://openstreetmap.org'>OpenStreetMap</a> contributors",
                },
            },
            layers: layers("protomaps", namedFlavor((dark) ? "dark" : "light"), { lang: "fr" }),
        })
    }

    public updateMarker(entity: EntityInfo){
        if(entity.last_known_lat && entity.last_known_long){
            if(!this.markers.has(entity.serial)){
                this._addMarker(entity)
            }

            this.markers.get(entity.serial)!
                .setLngLat([entity.last_known_long, entity.last_known_lat])
        }
    }

    public focus(entity: EntityInfo){
        const marker = this.markers.get(entity.serial);

        if(marker !== undefined){
            this.map.flyTo({
                center: marker.getLngLat(),
                zoom: 15
            })
        }
    }

    private _addMarker(entity: EntityInfo){
        const popup = new Popup({offset: 25})
            .setHTML(`
                <h1>Radio ABC123Z</h1><br />
                <i>Last seen at Long. 4.959351978617836, Lat. 50.40292135661877</i><br />
                <a href='http://crouton.net'>link</a>
            `)

        const marker = new Marker()
            .setLngLat([entity.last_known_long!, entity.last_known_lat!])
            .setPopup(popup)
            .addTo(this.map)

        this.markers.set(entity.serial, marker)

        console.log("Added location");
    }
}