import "./css/mainframe.css"
import MapLibre from "./MapLibre"
import Sidebar from "./Sidebar";

function Mainframe() {
    return(
        <div class={`mainframe`}>
            <MapLibre />
            <Sidebar />
        </div>
    )
}

export default Mainframe;