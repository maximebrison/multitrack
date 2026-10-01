import type { Setter } from "solid-js";
import type { NotifModel } from "../parts/UXElements";

export class UtilitiesController{
    private setNotif?: Setter<NotifModel|null>

    public init(setNotif: Setter<NotifModel|null>){
        this.setNotif = setNotif;
    }

    public notify(notif: NotifModel){
        this.setNotif!(null)
        this.setNotif!(notif)
    }
}