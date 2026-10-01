import { createContext, type ParentProps } from "solid-js";
import { SocketController } from "../controllers/SocketController";

export const SocketContext = createContext<SocketController>();

export const SocketProvider = (props: ParentProps) => {
    return(
        <SocketContext.Provider value={new SocketController()}>{props.children}</SocketContext.Provider>
    )
}