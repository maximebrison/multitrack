import { createContext, type ParentProps } from "solid-js";
import { UtilitiesController } from "../controllers/UtilitiesController";

export const UtilitiesContext = createContext<UtilitiesController>();

export const UtilitiesProvider = (props: ParentProps) => {
    return(
        <UtilitiesContext.Provider value={new UtilitiesController()}>{props.children}</UtilitiesContext.Provider>
    )
}