export type envelope = {
    dest: string,
    action: string,
    payload: string | null
}

export type pluginInfo = {
    id: string,
    ip_address: string | undefined,
    port: Number,
    actions: string[],
    text: boolean
}