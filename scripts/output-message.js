export function appendOutputMessage(msg, tipo = "info") {
    const output = document.getElementById("output");
    output.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = msg;
    p.className = "mensaje-pyodide " + tipo;
    output.appendChild(p);
}