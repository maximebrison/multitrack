import lightTheme from "../css/light.css?url"
import darkTheme from "../css/dark.css?url"

export class ThemeController{
    public dark!: boolean;
    private _extras: Function[] = [];

    constructor(){
        if(localStorage.getItem("dark") === null){
            this.dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
            localStorage.setItem("dark", `${this.dark}`)
        } else{
            this.dark = localStorage.getItem("dark") === "true";
        }
        
        this.switchTheme(true)
    }

    /**
     * Switches the theme then calls handlers loaded with **this.addExtraHandler()** for
     * additional theme switching behaviour (e.g. with MapLibre GL, which needs to reload
     * its layers and sprites).
     * 
     * @param init Force a value for the theme
     */
    public switchTheme(init: boolean = false){        
        const link = document.getElementById("theme") as HTMLLinkElement;
        let toDarkTheme: boolean;
        if(init){
            toDarkTheme = this.dark;
        } else{
            toDarkTheme = !this.dark;
            this.dark = !this.dark;
        }
        link.href = toDarkTheme ? darkTheme : lightTheme;
        localStorage.setItem("dark", `${this.dark}`)

        this._extras.forEach((fn) => fn());

        return this.dark;
    }

    /**
     * 
     * @param fn Handler to call when switching theme
     */
    public addExtraHandler(fn: Function){
        if(!this._extras.includes(fn)){
            this._extras.push(fn);
        }
    }
}