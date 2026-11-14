/* @refresh reload */
import { render } from 'solid-js/web'
import App from './App.tsx'
import './assets/fontawesome/css/all.css'
import { AppContextProvider } from './ctx/AppContext.tsx'

const root = document.getElementById('root')

render(() => <Index />, root!)

function Index(){
    return(
        <AppContextProvider>
            <App />
        </AppContextProvider>
    )
}
