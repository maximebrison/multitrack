export type envelope = {
    dest: string,
    action: string,
    payload: string | null
}

export type signedEnvelope = {
    client_id: string,
    envelope: envelope
}

export type driver = {
    type: string,
    main_ID: string,
    actions: string[],
    text: string,
    position: [number, number],
    status: string,
    last_updated: Date,
    ws_port: number,
    ws_ip : string
}

export type discovererCallbacks = {
    sendWSMessage: (se: signedEnvelope) => void
}

export type wsserverCallbacks = {
    onMessageReceived: (se: signedEnvelope) => void
}