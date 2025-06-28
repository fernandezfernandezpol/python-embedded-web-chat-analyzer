import { appendOutputMessage } from './output-message.js';

let pyodideReady = false;
let pyodide = null;

async function cargarPyodide() {
    appendOutputMessage("Cargando Pyodide...");
    try {
        pyodide = await loadPyodide();
        appendOutputMessage("Pyodide cargado correctamente.", "ok");
        await pyodide.loadPackage(['numpy', 'matplotlib']);
        appendOutputMessage("Paquetes cargados correctamente.", "ok");
        const basePath = window.location.pathname.endsWith('/')
            ? window.location.pathname
            : window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/') + 1);
        const urlAnalisis = window.location.origin + basePath + 'scripts/analisis.py';
        const resp = await fetch(urlAnalisis);
        if (!resp.ok) {
            throw new Error("No se pudo cargar analisis.py: " + resp.statusText);
        }
        await pyodide.runPythonAsync(await resp.text());
        pyodideReady = true;
        appendOutputMessage("Pyodide listo.", "ok");
    } catch (e) {
        pyodideReady = false;
        appendOutputMessage("Error al cargar Pyodide o los paquetes: " + e, "error");
    }
}
cargarPyodide();

export { pyodideReady, pyodide };