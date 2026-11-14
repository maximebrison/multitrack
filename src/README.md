# Dev

> You'll need **git**, **npm** and **python 3.9+** installed on your machine.

1. Create a new directory
2. Execute `git clone -b mbn's-cut-dev https://github.com/maximebrison/multitrack`

## Multitrack App

### Steps

1. Go to `/src/app/frontend` and execute `npm install && npm run dev`.
2. On another terminal instance, go to `/src/app` and execute `npm install && npm run dev`.
3. Open a web browser and navigate to http://localhost:5173 (or whatever port is used by Vite), you should then see the app in *development mode* (Vite dev server with Hot Module Reload).

Alternatively you can execute `npm run build` in `/src/app/frontend` to compile the front in `/src/app/dist`, which is served by `/src/app/app.ts`.

## Plugin demo

### Steps

1. Go to `/src/plugin_demo` and execute `python3 -m venv ./venv`.
2. Activate the *venv* with `source ./venv/bin/activate`.
3. Install *requirements* with `pip install -r ./requirements.txt`.
4. Execute `python3 ./plugin.py`.