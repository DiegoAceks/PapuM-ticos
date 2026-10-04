# Problema del camino mínimo — Algoritmo de Dijkstra

Aplicación interactiva (Streamlit) para el proyecto de 1AMA0726 (Matemática
Computacional): construcción de un grafo dirigido y acíclico, ejecución
paso a paso del algoritmo de Dijkstra, y determinación de todos los
caminos mínimos entre un vértice origen y un vértice destino.

## Requisitos

- **Python 3.10 o superior**. Descárgalo desde [python.org/downloads](https://www.python.org/downloads/)
  (NO lo instales desde Microsoft Store).
  - **Importante (Windows):** en el instalador, antes de darle a "Install Now",
    marca la casilla **"Add python.exe to PATH"**. Si no la marcas, los
    comandos de abajo no van a funcionar.

## Cómo descargar el proyecto

**Opción A — con Git:**
```
git clone <link-del-repositorio>
cd <nombre-de-la-carpeta>
```

**Opción B — sin Git (más simple):**
En GitHub, botón verde **"Code" → "Download ZIP"**, descomprime el archivo,
y abre esa carpeta en VS Code (`File > Open Folder...`).

## Instalación y ejecución

Abre una terminal dentro de la carpeta del proyecto (en VS Code:
`Terminal > New Terminal`) y ejecuta estos dos comandos:

```
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Esto abrirá automáticamente tu navegador en `http://localhost:8501` con la
aplicación corriendo.

## Problemas comunes

- **`pip` o `streamlit` "no se reconoce como un comando"**: usa siempre
  `python -m pip ...` y `python -m streamlit ...` en vez de `pip ...` y
  `streamlit ...` sueltos. Esto evita problemas de configuración del PATH
  en Windows.
- **`python` no se reconoce**: Python no está instalado o no se marcó
  "Add to PATH" durante la instalación. Reinstala desde python.org
  marcando esa casilla, y abre una terminal nueva después.
- **La app no me deja hacer zoom / arrastrar el grafo**: es normal, está
  desactivado a propósito para que el scroll de la página no interfiera.

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `app.py` | Interfaz (Streamlit + Plotly) |
| `grafo.py` | Representación del grafo (matriz de adyacencia) |
| `dijkstra.py` | Algoritmo de Dijkstra paso a paso + reconstrucción de caminos mínimos |
| `conectividad.py` | Verificación de componentes conexas |
| `requirements.txt` | Dependencias de Python |
| `.streamlit/config.toml` | Tema de colores de la interfaz |
