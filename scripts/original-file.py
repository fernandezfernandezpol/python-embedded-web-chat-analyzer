import re, sys, unicodedata, calendar
import numpy as np
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


def normalizar_texto(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )


def limpiar_linea(linea):
    linea = linea.strip()
    linea = re.sub(r'[\u200e\u200f\u202a-\u202e]', '', linea)
    return linea


def barplot_mensajes(palabras_buscadas, usuarios, personas):
    usuarios_año = defaultdict(lambda: defaultdict(int))
    for persona in personas:
        for periodo in usuarios[persona]:
            año = periodo.split("/")[-1]
            usuarios_año[persona][año] += usuarios[persona][periodo]
    
    años = sorted(set(año for datos in usuarios_año.values() for año in datos.keys()))
    for año in años:
        conteos = []
        for persona in personas:
            conteos.append(usuarios_año[persona].get(año, 0))

        if all(c == 0 for c in conteos):
            continue

        x = np.arange(len(personas))
        colormap = plt.get_cmap('jet')
        norm = x / (len(x) - 1 if len(x) > 1 else 1)
        colors = colormap(norm)

        plt.figure(figsize=(10,6))
        plt.bar(x, conteos, color=colors, width=0.3)
        plt.xticks(x, personas, rotation=45, ha='right')
        plt.title(f"Año {año}", fontsize=16, fontweight='bold')
        plt.ylabel(f"Veces que dijo '{palabras_buscadas}'", fontsize=14, fontweight='bold')
        plt.tight_layout()
        ax = plt.gca()
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        plt.show()


def progresion_mensajes(palabras_buscadas, usuarios, personas):
    datos = defaultdict(lambda: defaultdict(lambda: np.zeros(12, dtype=int)))  
    for persona in personas:
        for periodo, conteo in usuarios[persona].items():
            mes_str, año_str = periodo.split("/")
            mes = int(mes_str) - 1
            año = año_str
            datos[persona][año][mes] += conteo

    años = sorted({año for p in datos for año in datos[p]})
    colormap = plt.get_cmap('jet')
    n = len(personas)
    norm = np.linspace(0, 1, n)
    colors = colormap(norm)

    for año in años:
        conteos_totales = []
        for persona in personas:
            if año in datos[persona]:
                conteos_totales.append(datos[persona][año].sum())
            else:
                conteos_totales.append(0)

        if all(c == 0 for c in conteos_totales):
            continue
        plt.figure(figsize=(10,6))
        for i, persona in enumerate(personas):
            if año in datos[persona]:
                y = datos[persona][año]
            else:
                y = np.zeros(12, dtype=int)

            if np.any(y > 0):
                plt.plot(range(1,13), y, label=persona, color=colors[i], marker='o')

        plt.title(f"Año {año}", fontsize=16, fontweight='bold')
        plt.ylabel(f"Veces que dijo '{palabras_buscadas}'", fontsize=14, fontweight='bold')
        plt.xticks(range(1,13), [calendar.month_abbr[m] for m in range(1,13)])
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        ax = plt.gca()
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        plt.show()


def main():
    root = tk.Tk()
    root.withdraw()

    ruta_chat = filedialog.askopenfilename(
        title = "Selecciona un archivo .txt",
        filetypes = [("Archivos de texto", "*.txt")]
    )

    if not ruta_chat: sys.exit()

    nombre_grupo = ""
    usuarios = defaultdict(lambda: defaultdict(int))
    patron_mensajes = re.compile(r"\[\d{1,2}/(\d{1,2})/(\d{1,2}), \d{1,2}:\d{1,2}:\d{1,2}\] (.*?): (.+)", re.IGNORECASE)

    palabras_buscadas = input("Escribe que palabra quieres buscar: ").strip()
    palabra_normalizada = normalizar_texto(palabras_buscadas.lower())
    patron_palabras = re.compile(re.escape(palabra_normalizada), re.IGNORECASE)

    try:
        with open(ruta_chat, "r", encoding="utf-8") as chat:
            primera_linea = chat.readline()
            primera_linea = limpiar_linea(primera_linea)
            resultado = patron_mensajes.match(primera_linea)
            if resultado:
                nombre_grupo = resultado.group(3)

            for linea in chat:
                linea = limpiar_linea(linea)
                resultado = patron_mensajes.match(linea)
                if resultado:
                    mes, año, nombre, mensaje = resultado.groups()
                    if unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode().strip().casefold() == "tu": continue
                    periodo = f"{mes}/20{año}"
                    mensaje = normalizar_texto(mensaje.lower())
                    usuarios[nombre][periodo] += sum(1 for _ in patron_palabras.finditer(mensaje))

    except FileNotFoundError:
        print("Archivo no encontrado.")

    personas = sorted(usuarios.keys())
    if len(personas) > 2 and nombre_grupo in personas:
        personas = [p for p in personas if p != nombre_grupo]

    barplot_mensajes(palabras_buscadas, usuarios, personas)
    progresion_mensajes(palabras_buscadas, usuarios, personas)


if __name__ == "__main__":
    main()