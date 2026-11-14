import type { IncomingMessage } from "node:http"
import type { Database } from "../modules/Database.ts"
import type { Authenticator } from "../modules/Authenticator.ts"

export type Envelope = {
    dest: string,
    action: string,
    payload: string | null
}

export type SignedEnvelope = {
    client_id: string,
    envelope: Envelope
}

export interface EntityInfo{
    serial: number,
    plugin_id: number,
    friendly_name: string,
    last_update: number,
    last_known_lat: number | undefined,
    last_known_long: number | undefined,
    last_known_status: string | undefined,
    last_known_text: string | undefined
}

export type PluginInfo = {
    id: string,
    ip_address: string,
    port: number,
    actions: ActionModel[],
    bound: boolean
}

export type ActionModel = {
    label: string,
    model: {
        properties: Record<string,ModelProperty> | null,
        required: string[],
        title: string,
        type: string
    },
    scope: "remote" | "local",
    method: "GET" | "POST"
}

export type TextMessage = {
    msg: string
}

export type GPSPosition = {
    latitude: number,
    longitude: number
}

export type StatusUpdate = {
    status: string
}

export type PluginData = {
    plugin_id: string,
    entity_id: string,
    timestamp: number,
    type: "text" | "gps" | "status" | "err",
    success: boolean,
    data: TextMessage | GPSPosition | StatusUpdate | null
}

export type DiscovererCallbacks = {
    sendWSMessage: (se: signedEnvelope) => void
}

export type MultitrackServerCallbacks = {
    onDataReceived: (data: PluginData) => void
    onMessageReceived: (se: signedEnvelope) => void
}