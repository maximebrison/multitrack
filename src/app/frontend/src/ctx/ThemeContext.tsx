import { createContext, type ParentProps } from "solid-js";
import { ThemeController } from "../controllers/ThemeController";

export const ThemeContext = createContext<ThemeController>();

export const ThemeProvider = (props: ParentProps) => {
    return(
        <ThemeContext.Provider value={new ThemeController()}>{props.children}</ThemeContext.Provider>
    )
}