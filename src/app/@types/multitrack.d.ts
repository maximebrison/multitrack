export type envelope = {
    dest: string,
    action: string,
    payload: string | null
}

export type signedEnvelope = {
    client_id: string,
    envelope: envelope
}

export type pluginInfo = {
    ID: string,
    IP: string,
    port: number
}

export type dataFromPlugin = {
    type: string,
    main_ID: string,
    model: string,
    serial: string,
    last_updated: string,
    position: {
        timestamp: string,
        latitude: number,
        longitude: number
    } | null
    texts: string | string[] | null
    status: string | null
}

export type discovererCallbacks = {
    sendWSMessage: (se: signedEnvelope) => void
}

export type wsServerCallbacks = {
    onMessageReceived: (se: signedEnvelope) => void
}

export type httpServerCallbacks = {
    onDataReceived: (data: any) => void
}