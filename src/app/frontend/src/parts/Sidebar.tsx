import "./sidebar.css"

function Sidebar() {
    return(
        <div class="sidebar">
                <SidebarItem />
        </div>
    )
}

function SidebarItem() {
    return(
        <div class="sidebar-item">
            <h1>Radio <i>AYT652B</i></h1>
            <table>
                <tbody>
                    <tr>
                        <th>Type</th>
                        <td>radio</td>
                    </tr>
                    <tr>
                        <th>Model</th>
                        <td>ICOM AB246</td>
                    </tr>
                    <tr>
                        <th>Serial</th>
                        <td>dn2765</td>
                    </tr>
                    <tr>
                        <th>Last updated</th>
                        <td>7 minutes ago</td>
                    </tr>
                    <tr>
                        <th>Position</th>
                        <td>{"[50.8335, 4.36464]"}</td>
                    </tr>
                    <tr>
                        <th>Text</th>
                        <td>Hello World !</td>
                    </tr>
                    <tr>
                        <th>Status</th>
                        <td>Alive</td>
                    </tr>
                </tbody>
            </table>
            <form onsubmit={(e) => e.preventDefault()}>
                <input type="text"></input>
                <input type="submit" value={"Send"}></input>
            </form>
            <div class="buttons">
                <button>Stun</button>
                <button>Kill</button>
                <button>Revive</button>
            </div>
        </div>
    )
}

export default Sidebar;