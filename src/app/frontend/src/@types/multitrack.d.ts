export type Envelope = {
    dest: string,
    action: string,
    payload: string | null
}

export type EntityInfo = {
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

type ModelProperty = {
    title: string,
    type: string
}