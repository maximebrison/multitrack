import { createContext, type ParentProps } from "solid-js";
import { ContextController } from "../controllers/_ContextController";

export const AppContext = createContext<ContextController>();

export const AppContextProvider = (props: ParentProps) => {
    return(
        <AppContext.Provider value={new ContextController()}>{props.children}</AppContext.Provider>
    )
}