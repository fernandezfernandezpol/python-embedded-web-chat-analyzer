import { appendOutputMessage } from './output-message.js';
import { pyodideReady, pyodide } from './pyodide-loader.js';

let imagenes = [];
let imagenActual = 0;
let tipoActual = 'barplot';

function mostrarImagen() {
    const output = document.getElementById("output");
    const filtradas = imagenes.filter(img => img.tipo === tipoActual);

    output.classList.remove("imagenes-cargadas");
    output.innerHTML = "";

    if (!filtradas.length) {
        appendOutputMessage("No hay imágenes para este tipo.", "info");
        return;
    }
    output.classList.add("imagenes-cargadas");

    imagenActual = Math.max(0, Math.min(imagenActual, filtradas.length - 1));

    const controls = document.createElement("div");
    controls.className = "imagen-controls";

    const btnPrev = document.createElement("button");
    btnPrev.textContent = "‹";
    btnPrev.onclick = () => { imagenActual--; mostrarImagen(); };
    btnPrev.disabled = imagenActual === 0;

    const btnBarplot = document.createElement("button");
    btnBarplot.textContent = "Barras";
    btnBarplot.className = "btn-tipo" + (tipoActual === "barplot" ? " tipo-activo" : "");
    btnBarplot.onclick = () => {
        if (tipoActual !== "barplot") {
            tipoActual = "barplot";
            imagenActual = 0;
            mostrarImagen();
        }
    };

    const btnProgresion = document.createElement("button");
    btnProgresion.textContent = "Progresión";
    btnProgresion.className = "btn-tipo" + (tipoActual === "progresion" ? " tipo-activo" : "");
    btnProgresion.onclick = () => {
        if (tipoActual !== "progresion") {
            tipoActual = "progresion";
            imagenActual = 0;
            mostrarImagen();
        }
    };

    const btnNext = document.createElement("button");
    btnNext.textContent = "›";
    btnNext.onclick = () => { imagenActual++; mostrarImagen(); };
    btnNext.disabled = imagenActual === filtradas.length - 1;

    controls.appendChild(btnPrev);
    controls.appendChild(btnBarplot);
    controls.appendChild(btnProgresion);
    controls.appendChild(btnNext);

    output.appendChild(controls);

    const img = document.createElement("img");
    img.src = "data:image/png;base64," + filtradas[imagenActual].b64;
    img.className = "imagen-grande";
    output.appendChild(img);

    const pie = document.createElement("div");
    pie.className = "imagen-pie";
    pie.textContent = `Imagen ${imagenActual + 1} de ${filtradas.length} (${tipoActual === "barplot" ? "Barras" : "Progresión"})`;
    output.appendChild(pie);
}

async function procesar() {
    const output = document.getElementById("output");
    output.classList.remove("imagenes-cargadas");
    output.innerHTML = "";

    if (!pyodideReady) {
        appendOutputMessage("Pyodide no está listo.", "error");
        return;
    }

    const fileInput = document.getElementById("txtfile");
    const palabra = document.getElementById("palabra").value.trim();
    if (!fileInput.files.length || !palabra) {
        appendOutputMessage("Selecciona un archivo y escribe una palabra.", "error");
        return;
    }
    const reader = new FileReader();
    reader.onload = async function(event) {
        const texto = event.target.result;
        try {
            const imgs_base64 = await pyodide.runPythonAsync(
                `analizar_chat(${JSON.stringify(texto)}, ${JSON.stringify(palabra)})`
            );
            let arr = imgs_base64.toJs ? imgs_base64.toJs() : imgs_base64;
            const n = Math.floor(arr.length / 2);
            imagenes = [];
            for (let i = 0; i < arr.length; i++) {
                imagenes.push({
                    b64: arr[i],
                    tipo: i < n ? "barplot" : "progresion"
                });
            }
            tipoActual = "barplot";
            imagenActual = 0;
            mostrarImagen();
        } catch(e) {
            output.classList.remove("imagenes-cargadas");
            appendOutputMessage("Error en el procesamiento: " + e, "error");
        }
    };
    reader.onerror = function(e) {
        output.classList.remove("imagenes-cargadas");
        appendOutputMessage("Error al leer el archivo: " + e, "error");
    }
    reader.readAsText(fileInput.files[0]);
}
window.procesar = procesar;