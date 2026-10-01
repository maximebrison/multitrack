/* @refresh reload */
import { render } from 'solid-js/web'
import App from './App.tsx'
import './assets/fontawesome/css/all.css'
import { SocketProvider } from './ctx/SocketContext.tsx'
import { ThemeProvider } from './ctx/ThemeContext.tsx'
import { UtilitiesProvider } from './ctx/UtilitiesContext.tsx'

const root = document.getElementById('root')

render(() => <Index />, root!)

function Index(){
    return(
        <SocketProvider>
            <ThemeProvider>
                <UtilitiesProvider>
                    <App />
                </UtilitiesProvider>
            </ThemeProvider>
        </SocketProvider>
    )
}
