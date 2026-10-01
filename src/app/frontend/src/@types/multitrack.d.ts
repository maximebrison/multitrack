export type envelope = {
    dest: string,
    action: string,
    payload: string | null
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