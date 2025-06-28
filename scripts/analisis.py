import re, unicodedata, calendar
import numpy as np
from collections import defaultdict
import matplotlib
matplotlib.use("module://matplotlib.backends.backend_agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import io
import base64

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
    imagenes = []
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
        fig, ax = plt.subplots(figsize=(10,6))
        ax.bar(x, conteos, color=colors, width=0.3)
        ax.set_xticks(x)
        ax.set_xticklabels(personas, rotation=45, ha='right')
        ax.set_title(f"Año {año}", fontsize=16, fontweight='bold')
        ax.set_ylabel(f"Veces que dijo '{palabras_buscadas}'", fontsize=14, fontweight='bold')
        fig.tight_layout()
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        imagenes.append(img_str)
    return imagenes

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
    imagenes = []
    for año in años:
        conteos_totales = []
        for persona in personas:
            if año in datos[persona]:
                conteos_totales.append(datos[persona][año].sum())
            else:
                conteos_totales.append(0)
        if all(c == 0 for c in conteos_totales):
            continue
        fig, ax = plt.subplots(figsize=(10,6))
        for i, persona in enumerate(personas):
            if año in datos[persona]:
                y = datos[persona][año]
            else:
                y = np.zeros(12, dtype=int)
            if np.any(y > 0):
                ax.plot(range(1,13), y, label=persona, color=colors[i], marker='o')
        ax.set_title(f"Año {año}", fontsize=16, fontweight='bold')
        ax.set_ylabel(f"Veces que dijo '{palabras_buscadas}'", fontsize=14, fontweight='bold')
        ax.set_xticks(range(1,13))
        ax.set_xticklabels([calendar.month_abbr[m] for m in range(1,13)])
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        fig.tight_layout()
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        imagenes.append(img_str)
    return imagenes

def analizar_chat(texto_chat, palabras_buscadas):
    usuarios = defaultdict(lambda: defaultdict(int))
    patron_mensajes = re.compile(r"\[\d{1,2}/(\d{1,2})/(\d{1,2}), \d{1,2}:\d{1,2}:\d{1,2}\] (.*?): (.+)", re.IGNORECASE)

    palabra_normalizada = normalizar_texto(palabras_buscadas.lower())
    patron_palabras = re.compile(re.escape(palabra_normalizada), re.IGNORECASE)

    lineas = texto_chat.splitlines()
    nombre_grupo = ""
    if lineas:
        primera_linea = limpiar_linea(lineas[0])
        resultado = patron_mensajes.match(primera_linea)
        if resultado:
            nombre_grupo = resultado.group(3)
    for linea in lineas:
        linea = limpiar_linea(linea)
        resultado = patron_mensajes.match(linea)
        if resultado:
            mes, año, nombre, mensaje = resultado.groups()
            if unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode().strip().casefold() == "tu": continue
            periodo = f"{mes}/20{año}"
            mensaje = normalizar_texto(mensaje.lower())
            usuarios[nombre][periodo] += sum(1 for _ in patron_palabras.finditer(mensaje))

    personas = sorted(usuarios.keys())
    if len(personas) > 2 and nombre_grupo in personas:
        personas = [p for p in personas if p != nombre_grupo]

    imgs1 = barplot_mensajes(palabras_buscadas, usuarios, personas)
    imgs2 = progresion_mensajes(palabras_buscadas, usuarios, personas)
    return imgs1 + imgs2