"""
app.py
Interfaz interactiva (Streamlit) para el proyecto "Problema del camino
mínimo" - algoritmo de Dijkstra.

Curso: 1AMA0726 - Matemática Computacional
"""

import hashlib
import json
import random
import time

import streamlit as st
import networkx as nx

from grafo import Grafo
from conectividad import existe_camino
from dijkstra import ejecutar_dijkstra, reconstruir_caminos, INFINITO

st.set_page_config(
    page_title="Dijkstra · Camino mínimo",
    page_icon="🧭",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Paleta de colores (única fuente de verdad para toda la app)
# ---------------------------------------------------------------------------

COLOR = {
    "origen": "#5EEAD4",         # turquesa pastel
    "destino": "#FDA4AF",        # rosa coral pastel
    "actual": "#FCD34D",         # amarillo durazno pastel
    "visitado": "#93C5FD",       # celeste pastel
    "pendiente": "#F1F5F9",      # gris perla
    "arista": "#CBD5E1",         # gris azulado suave
    "arista_resaltada": "#FB7185",  # coral más saturado, para que el camino final resalte
    "primario": "#C4B5FD",       # lavanda pastel (botones, pestañas activas)
}

# ---------------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------------

st.markdown(f"""
<style>
    /* Fondos translúcidos (no colores sólidos fijos) para que se vea bien
       tanto en tema claro como oscuro de Streamlit. */
    .main > div {{ padding-top: 1rem; max-width: 100%; }}
    h1 {{ font-weight: 800; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; flex-wrap: wrap; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(148, 163, 184, 0.12);
        border-radius: 10px 10px 0 0;
        padding: 10px 16px;
        font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR['primario']}33 !important;
    }}

    div[data-testid="stMetric"] {{
        background-color: rgba(148, 163, 184, 0.10);
        border: 1px solid rgba(148, 163, 184, 0.35);
        border-radius: 14px;
        padding: 12px 10px;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 14px; }}

    .leyenda {{
        display: flex; flex-wrap: wrap; gap: 8px 16px; margin: 4px 0 12px 0;
        font-size: 0.85rem; opacity: 0.9;
    }}
    .dot {{
        display: inline-block; width: 11px; height: 11px; border-radius: 50%;
        margin-right: 5px; vertical-align: middle;
    }}
</style>
""", unsafe_allow_html=True)


def leyenda_grafo():
    items = [
        (COLOR["origen"], "Origen"),
        (COLOR["destino"], "Destino"),
        (COLOR["actual"], "Nodo en proceso"),
        (COLOR["visitado"], "Visitado"),
        (COLOR["pendiente"], "Pendiente"),
    ]
    html = '<div class="leyenda">' + "".join(
        f'<span><span class="dot" style="background:{c}"></span>{t}</span>'
        for c, t in items
    ) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Funciones de dibujo
# ---------------------------------------------------------------------------

def construir_grafo_networkx(grafo):
    G = nx.DiGraph()
    G.add_nodes_from(range(grafo.n))
    for i, j, peso in grafo.obtener_aristas():
        G.add_edge(i, j, weight=peso)
    return G


def calcular_layout(grafo):
    """
    Calcula la posición de los nodos mediante un layout jerárquico propio
    (sin depender de librerías externas como Graphviz): cada nodo se ubica
    en una columna según la longitud del camino más largo que llega a él
    desde algún nodo sin predecesores (su "nivel"), y los nodos de un
    mismo nivel se distribuyen verticalmente. Cuando un nivel tiene un
    solo nodo, se aplica un pequeño desplazamiento en zigzag para evitar
    que cadenas largas queden perfectamente alineadas, lo que haría que
    las aristas "salteadas" se superpongan visualmente con las directas.
    """
    niveles = [0] * grafo.n
    for v in range(grafo.n):
        for u in range(v):
            if grafo.matriz[u][v] != 0:
                niveles[v] = max(niveles[v], niveles[u] + 1)

    por_nivel = {}
    for v in range(grafo.n):
        por_nivel.setdefault(niveles[v], []).append(v)

    layout = {}
    espacio_x, espacio_y = 2.6, 1.5
    for nivel, nodos in por_nivel.items():
        cantidad = len(nodos)
        for i, v in enumerate(nodos):
            if cantidad == 1:
                y = espacio_y * 0.6 * ((v % 3) - 1)
            else:
                y = (i - (cantidad - 1) / 2) * espacio_y
            layout[v] = (nivel * espacio_x, y)
    return layout


_HTML_GRAFO = r"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<!-- __KEY__ -->
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; background: transparent;
               font-family: "Segoe UI", system-ui, -apple-system, Arial, sans-serif; }
  #wrap { box-sizing: border-box; border: 1px solid #E2E8F0; border-radius: 14px;
          background: #FFFFFF; overflow: hidden; }
  #bar { box-sizing: border-box; height: 30px; display: flex; justify-content: space-between;
         align-items: center; gap: 8px; padding: 0 10px; font-size: 12px; color: #64748B;
         border-bottom: 1px solid #F1F5F9; }
  #reset { font: inherit; color: #475569; background: #F5F3FF; border: 1px solid #DDD6FE;
           border-radius: 8px; padding: 2px 10px; cursor: pointer; }
  #reset:hover { background: #EDE9FE; }
  svg { display: block; width: 100%; height: 420px; user-select: none; -webkit-user-select: none; }
  .node { cursor: grab; touch-action: none; }
  .node.drag { cursor: grabbing; }
  .node:hover circle { stroke-width: 3.5; }
</style></head>
<body>
<div id="wrap">
  <div id="bar">
    <span>🖱️ Arrastra los nodos para ordenarlos (opcional)</span>
    <button id="reset" type="button">↺ Restablecer posiciones</button>
  </div>
  <svg id="g" viewBox="0 0 800 420" role="img" aria-label="Grafo dirigido con pesos"></svg>
</div>
<script>
(function () {
  var D = __DATOS__;
  var NS = "http://www.w3.org/2000/svg";
  var H = 420, PX = 44, PY = 40, R = 22, GAP = 3;
  var wrap = document.getElementById("wrap");
  var svg = document.getElementById("g");
  var N = D.n, W = 800;

  function el(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) { e.setAttribute(k, attrs[k]); }
    if (parent) { parent.appendChild(e); }
    return e;
  }
  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }

  // Posición inicial: el layout jerárquico calculado en Python, normalizado a 0..1.
  var xs = D.pos.map(function (p) { return p[0]; });
  var ys = D.pos.map(function (p) { return p[1]; });
  var minx = Math.min.apply(null, xs), maxx = Math.max.apply(null, xs);
  var miny = Math.min.apply(null, ys), maxy = Math.max.apply(null, ys);
  var defecto = D.pos.map(function (p) {
    return [maxx > minx ? (p[0] - minx) / (maxx - minx) : 0.5,
            maxy > miny ? 1 - (p[1] - miny) / (maxy - miny) : 0.5];
  });

  // Las posiciones movidas por el usuario se guardan en el navegador (si está permitido).
  function cargar() {
    try {
      var s = localStorage.getItem(D.key);
      if (!s) { return null; }
      var a = JSON.parse(s);
      if (Array.isArray(a) && a.length === N && a.every(function (p) {
        return Array.isArray(p) && isFinite(p[0]) && isFinite(p[1]);
      })) {
        return a.map(function (p) { return [clamp(+p[0], 0, 1), clamp(+p[1], 0, 1)]; });
      }
    } catch (e) { /* sin almacenamiento: se usa la posición por defecto */ }
    return null;
  }
  function guardar() {
    try { localStorage.setItem(D.key, JSON.stringify(pos)); } catch (e) { /* ignorar */ }
  }
  var pos = cargar() || defecto.map(function (p) { return p.slice(); });

  function px(i) { return PX + pos[i][0] * (W - 2 * PX); }
  function py(i) { return PY + pos[i][1] * (H - 2 * PY); }

  // Puntas de flecha (una normal y una más grande para los caminos mínimos).
  var defs = el("defs", {}, svg);
  function marcador(id, color, L) {
    var m = el("marker", { id: id, viewBox: "0 0 10 10", refX: 0, refY: 5,
      markerUnits: "userSpaceOnUse", markerWidth: L, markerHeight: L, orient: "auto" }, defs);
    el("path", { d: "M0,0 L10,5 L0,10 z", fill: color }, m);
  }
  marcador("ah", D.colores.arista, 12);
  marcador("ahh", D.colores.resaltada, 16);

  var capaAristas = el("g", {}, svg);
  var capaEtiquetas = el("g", {}, svg);
  var capaNodos = el("g", {}, svg);

  // Los caminos resaltados se dibujan al final para quedar por encima.
  var aristas = D.edges.slice().sort(function (a, b) {
    return (a.hl ? 1 : 0) - (b.hl ? 1 : 0);
  }).map(function (e) {
    var hl = !!e.hl;
    var linea = el("line", { stroke: hl ? D.colores.resaltada : D.colores.arista,
      "stroke-width": hl ? 4 : 1.8, "marker-end": "url(#" + (hl ? "ahh" : "ah") + ")" }, capaAristas);
    var g = el("g", {}, capaEtiquetas);
    var ancho = String(e.w).length * 8 + 14;
    el("rect", { x: -ancho / 2, y: -9, width: ancho, height: 18, rx: 6,
      fill: "#FFFFFF", "fill-opacity": 0.92, stroke: "rgba(0,0,0,0.10)" }, g);
    var t = el("text", { "text-anchor": "middle", dy: "0.35em", "font-size": 12,
      "font-weight": 700, fill: "#1E293B" }, g);
    t.textContent = e.w;
    return { e: e, linea: linea, g: g, AL: hl ? 16 : 12 };
  });

  var nodos = D.nodes.map(function (n, i) {
    var g = el("g", { "class": "node" }, capaNodos);
    var ti = el("title", {}, g);
    ti.textContent = n.tip;
    el("circle", { r: R, fill: n.fill, stroke: n.stroke, "stroke-width": 2.5 }, g);
    var t = el("text", { "text-anchor": "middle", dy: "0.35em", "font-size": 15,
      "font-weight": 800, fill: "#0F172A", "pointer-events": "none" }, g);
    t.textContent = n.id;
    g.addEventListener("pointerdown", function (ev) { empezar(ev, i, g); });
    g.addEventListener("pointermove", mover);
    g.addEventListener("pointerup", terminar);
    g.addEventListener("pointercancel", terminar);
    g.addEventListener("lostpointercapture", terminar);
    return g;
  });

  // Las flechas y los pesos siguen a los nodos: se recalculan a partir de sus posiciones.
  function actualizarAristas() {
    aristas.forEach(function (a) {
      var x1 = px(a.e.u), y1 = py(a.e.u), x2 = px(a.e.v), y2 = py(a.e.v);
      var dx = x2 - x1, dy = y2 - y1, d = Math.sqrt(dx * dx + dy * dy);
      if (d < 2 * (R + GAP) + a.AL + 2) {          // nodos casi encimados: no cabe la flecha
        a.linea.style.display = "none"; a.g.style.display = "none"; return;
      }
      a.linea.style.display = ""; a.g.style.display = "";
      var ux = dx / d, uy = dy / d;
      var sx = x1 + ux * (R + GAP), sy = y1 + uy * (R + GAP);   // borde del nodo origen
      var tx = x2 - ux * (R + GAP), ty = y2 - uy * (R + GAP);   // punta, en el borde del destino
      a.linea.setAttribute("x1", sx); a.linea.setAttribute("y1", sy);
      a.linea.setAttribute("x2", tx - ux * a.AL); a.linea.setAttribute("y2", ty - uy * a.AL);
      a.g.setAttribute("transform", "translate(" + (sx + tx) / 2 + "," + (sy + ty) / 2 + ")");
    });
  }
  function dibujar() {
    for (var i = 0; i < N; i++) {
      nodos[i].setAttribute("transform", "translate(" + px(i) + "," + py(i) + ")");
    }
    actualizarAristas();
  }
  function ajustarAncho() {
    var w = Math.max(wrap.clientWidth, 320);
    if (w !== W || !svg.getAttribute("data-ok")) {
      W = w;
      svg.setAttribute("viewBox", "0 0 " + W + " " + H);
      svg.setAttribute("data-ok", "1");
    }
  }

  // Arrastre con mouse o dedo (pointer events).
  var arr = null;
  function puntoSVG(ev) {
    var m = svg.getScreenCTM && svg.getScreenCTM();
    if (!m) { return null; }
    var pt = svg.createSVGPoint();
    pt.x = ev.clientX; pt.y = ev.clientY;
    return pt.matrixTransform(m.inverse());
  }
  function empezar(ev, i, g) {
    if (ev.button !== undefined && ev.button !== 0) { return; }
    var p = puntoSVG(ev);
    if (!p) { return; }
    ev.preventDefault();
    arr = { i: i, g: g, dx: px(i) - p.x, dy: py(i) - p.y };
    g.classList.add("drag");
    capaNodos.appendChild(g);                       // el nodo arrastrado queda al frente
    if (g.setPointerCapture && ev.pointerId !== undefined) {
      try { g.setPointerCapture(ev.pointerId); } catch (e) { /* ignorar */ }
    }
  }
  function mover(ev) {
    if (!arr) { return; }
    if (ev.pointerType === "mouse" && ev.buttons === 0) { terminar(); return; }
    var p = puntoSVG(ev);
    if (!p) { return; }
    pos[arr.i][0] = clamp((p.x + arr.dx - PX) / (W - 2 * PX), 0, 1);
    pos[arr.i][1] = clamp((p.y + arr.dy - PY) / (H - 2 * PY), 0, 1);
    dibujar();
  }
  function terminar() {
    if (!arr) { return; }
    arr.g.classList.remove("drag");
    arr = null;
    guardar();
  }

  document.getElementById("reset").addEventListener("click", function () {
    pos = defecto.map(function (p) { return p.slice(); });
    try { localStorage.removeItem(D.key); } catch (e) { /* ignorar */ }
    dibujar();
  });

  function alRedimensionar() { ajustarAncho(); dibujar(); }
  alRedimensionar();
  if (typeof ResizeObserver !== "undefined") { new ResizeObserver(alRedimensionar).observe(wrap); }
  else { window.addEventListener("resize", alRedimensionar); }
})();
</script>
</body></html>"""


def _mostrar_html(html, alto):
    """Muestra HTML en un iframe: st.iframe (Streamlit actual) o, en versiones
    antiguas, components.html."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=alto)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=alto)


def dibujar_grafo(grafo, layout, origen=None, destino=None, actual=None,
                   visitados=None, aristas_resaltadas=None, distancias=None,
                   key=None):
    """
    Dibuja el grafo como un SVG interactivo: los nodos se pueden arrastrar con
    el mouse (o el dedo) y las flechas y los pesos los siguen. Es opcional: si
    no se mueve nada, se ve el layout jerárquico calculado en calcular_layout.
    Las posiciones movidas se recuerdan en el navegador mientras el grafo (sus
    conexiones) no cambie, así que se conservan entre pasos y pestañas.
    """
    visitados = visitados or []
    aristas_resaltadas = set(aristas_resaltadas or [])

    nodos = []
    for i in range(grafo.n):
        if i == origen:
            fill = COLOR["origen"]
        elif i == destino:
            fill = COLOR["destino"]
        elif i == actual:
            fill = COLOR["actual"]
        elif i in visitados:
            fill = COLOR["visitado"]
        else:
            fill = COLOR["pendiente"]
        borde = "#1E293B" if i in (origen, destino, actual) else "#94A3B8"
        info = f"Vértice {i}"
        if distancias is not None:
            d = distancias[i]
            info += f"\nDistancia mínima: {'∞' if d == INFINITO else d}"
        nodos.append({"id": i, "fill": fill, "stroke": borde, "tip": info})

    aristas = [
        {"u": u, "v": v, "w": peso, "hl": (u, v) in aristas_resaltadas}
        for u, v, peso in grafo.obtener_aristas()
    ]
    # Las posiciones guardadas dependen solo de las conexiones del grafo.
    firma = hashlib.md5(
        ",".join(f"{a['u']}-{a['v']}" for a in aristas).encode()
    ).hexdigest()[:10]

    datos = {
        "n": grafo.n,
        "key": f"dijkstra-pos-{grafo.n}-{firma}",
        "pos": [[float(layout[i][0]), float(layout[i][1])] for i in range(grafo.n)],
        "nodes": nodos,
        "edges": aristas,
        "colores": {"arista": COLOR["arista"], "resaltada": COLOR["arista_resaltada"]},
    }
    html = (
        _HTML_GRAFO
        .replace("__KEY__", str(key))
        .replace("__DATOS__", json.dumps(datos).replace("<", "\\u003c"))
    )
    _mostrar_html(html, 456)


# ---------------------------------------------------------------------------
# Estado de la sesión
# ---------------------------------------------------------------------------

for clave, valor in {
    "grafo": None, "layout": None, "pasos_dijkstra": None, "paso_actual": 0,
    "origen_prev": None, "destino_prev": None,
}.items():
    if clave not in st.session_state:
        st.session_state[clave] = valor


def reiniciar_ejecucion():
    st.session_state.pasos_dijkstra = None
    st.session_state.paso_actual = 0


# ---------------------------------------------------------------------------
# Barra lateral: configuración del grafo
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### ⚙️ Configuración del grafo")
    n = st.number_input("Número de nodos (n)", min_value=7, max_value=16, value=7, step=1)
    modo = st.radio("Modo de generación", ["🎲 Aleatorio", "✍️ Manual"], horizontal=False)

    if st.session_state.grafo is None or st.session_state.grafo.n != int(n):
        st.session_state.grafo = Grafo(int(n))
        st.session_state.layout = None
        reiniciar_ejecucion()

    grafo = st.session_state.grafo

    st.divider()

    if modo.startswith("🎲"):
        st.caption("Genera un grafo dirigido y acíclico con aristas y pesos al azar.")
        densidad = st.slider(
            "Densidad de conexiones", 0.1, 0.8, 0.4, 0.05,
            help="Una densidad más baja genera grafos más simples y fáciles de leer; "
                 "una densidad más alta genera más aristas y caminos alternativos."
        )
        semilla_txt = st.text_input(
            "Semilla aleatoria (opcional)",
            help="Fija un valor para poder reproducir exactamente el mismo grafo más adelante."
        )
        if st.button("🎲 Generar grafo aleatorio", width="stretch", type="primary"):
            if semilla_txt.strip():
                random.seed(semilla_txt.strip())
            grafo.limpiar()
            grafo.generar_aleatorio(densidad=densidad)
            st.session_state.layout = None
            reiniciar_ejecucion()

    else:
        st.caption(
            "Toda arista debe ir de un nodo con índice menor a uno con índice "
            "mayor (i < j), lo que garantiza que el grafo sea dirigido y "
            "acíclico por construcción."
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            o = st.number_input("Origen", min_value=0, max_value=int(n) - 2, value=0)
        with col2:
            d = st.number_input("Destino", min_value=int(o) + 1, max_value=int(n) - 1, value=int(n) - 1)
        with col3:
            p = st.number_input("Peso", min_value=1, value=1)

        if st.button("➕ Agregar arista", width="stretch", type="primary"):
            try:
                grafo.agregar_arista(int(o), int(d), int(p))
                st.session_state.layout = None
                reiniciar_ejecucion()
                st.success(f"Arista agregada: {o} → {d} (peso {p})")
            except ValueError as e:
                st.error(str(e))

        aristas_actuales = grafo.obtener_aristas()
        if aristas_actuales:
            st.write("**Aristas actuales:**")
            opciones = [f"{i} → {j}  (peso {w})" for i, j, w in aristas_actuales]
            seleccion = st.selectbox("Eliminar una arista", opciones)
            if st.button("🗑️ Eliminar arista seleccionada", width="stretch"):
                idx = opciones.index(seleccion)
                i, j, _ = aristas_actuales[idx]
                grafo.eliminar_arista(i, j)
                reiniciar_ejecucion()
                st.rerun()

        if st.button("♻️ Reiniciar grafo (quitar todas las aristas)", width="stretch"):
            grafo.limpiar()
            reiniciar_ejecucion()
            st.rerun()

    st.divider()
    st.caption(f"Nodos: **{grafo.n}**  ·  Aristas: **{len(grafo.obtener_aristas())}**")


# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------

st.markdown(
    f"<h1>🧭 Problema del camino mínimo</h1>"
    f"<p style='color:#64748B; margin-top:-8px;'>Algoritmo de Dijkstra sobre un grafo dirigido y acíclico — "
    f"ejecución interactiva, paso a paso.</p>",
    unsafe_allow_html=True,
)

grafo = st.session_state.grafo

if not grafo.obtener_aristas():
    st.info("👈 Agrega aristas manualmente o genera un grafo aleatorio desde el panel lateral para comenzar.")
    st.stop()

if st.session_state.layout is None:
    st.session_state.layout = calcular_layout(grafo)
layout = st.session_state.layout

tab_grafo, tab_ejecucion, tab_resultado = st.tabs(
    ["🕸️ 1. Grafo y selección", "▶️ 2. Ejecución paso a paso", "🏁 3. Solución"]
)

# ---------------------------------------------------------------------------
# Pestaña 1: Grafo y selección de origen/destino
# ---------------------------------------------------------------------------

with tab_grafo:
    col_sel, col_vis = st.columns([1, 2])

    with col_sel:
        st.markdown("#### Selecciona los vértices")
        origen = st.selectbox("Vértice origen", options=list(range(grafo.n)), key="origen_sel")
        destino = st.selectbox(
            "Vértice destino", options=list(range(grafo.n)),
            index=grafo.n - 1, key="destino_sel"
        )

        if (origen, destino) != (st.session_state.origen_prev, st.session_state.destino_prev):
            reiniciar_ejecucion()
            st.session_state.origen_prev = origen
            st.session_state.destino_prev = destino

        if origen == destino:
            st.warning("⚠️ El vértice origen y destino no pueden ser el mismo.")
        elif not existe_camino(grafo, origen, destino):
            st.error("❌ No existe ningún camino entre el origen y el destino seleccionados.")
        else:
            st.success("✅ Existe conexión entre ambos vértices. Ve a la pestaña **2** para ejecutar Dijkstra.")

        st.markdown("#### Matriz de adyacencia")
        with st.expander("Ver matriz", expanded=False):
            st.dataframe(
                [[grafo.matriz[i][j] for j in range(grafo.n)] for i in range(grafo.n)],
                width="stretch",
            )

    with col_vis:
        leyenda_grafo()
        dibujar_grafo(grafo, layout, origen=origen, destino=destino, key="grafo_tab1")

# ---------------------------------------------------------------------------
# Pestaña 2: Ejecución paso a paso
# ---------------------------------------------------------------------------

with tab_ejecucion:
    if origen == destino or not existe_camino(grafo, origen, destino):
        st.info("Selecciona un origen y destino válidos en la pestaña **1** para habilitar la ejecución.")
    else:
        col_start, col_auto, col_vel = st.columns([1.3, 1, 1])
        with col_start:
            if st.button("▶️ Iniciar / reiniciar ejecución", width="stretch", type="primary"):
                distancias, predecesores, pasos = ejecutar_dijkstra(grafo, origen)
                st.session_state.pasos_dijkstra = (distancias, predecesores, pasos)
                st.session_state.paso_actual = 0
        with col_auto:
            autoplay = st.checkbox("⏱️ Reproducción automática")
        with col_vel:
            velocidad = st.slider("Segundos/paso", 0.3, 3.0, 1.0, 0.1, disabled=not autoplay)

        if st.session_state.pasos_dijkstra is not None:
            distancias, predecesores, pasos = st.session_state.pasos_dijkstra
            total_pasos = len(pasos)
            idx = st.session_state.paso_actual

            st.progress(idx / total_pasos if total_pasos else 0,
                        text=f"Paso {idx} de {total_pasos}")

            col_prev, col_next = st.columns(2)
            with col_prev:
                if st.button("⬅️ Paso anterior", disabled=(idx == 0), width="stretch"):
                    st.session_state.paso_actual = max(0, idx - 1)
                    st.rerun()
            with col_next:
                if st.button("Siguiente paso ➡️", disabled=(idx >= total_pasos), width="stretch"):
                    st.session_state.paso_actual = min(total_pasos, idx + 1)
                    st.rerun()

            idx = st.session_state.paso_actual
            col_izq, col_der = st.columns([1, 1.2])

            if idx == 0:
                m1, m2, m3 = st.columns(3)
                m1.metric("Nodo actual", "—")
                m2.metric("Visitados", 0)
                m3.metric("Iteración", "0 / " + str(total_pasos))
                with col_izq:
                    st.info(
                        "**Estado inicial:** la distancia del vértice origen se fija en 0 "
                        "y la de los demás vértices en infinito (∞)."
                    )
                with col_der:
                    leyenda_grafo()
                    dibujar_grafo(grafo, layout, origen=origen, destino=destino, key="grafo_tab2_inicial")
            else:
                if idx == 1:
                    distancias_antes = [0 if v == origen else INFINITO for v in range(grafo.n)]
                    visitados_antes = [False] * grafo.n
                else:
                    distancias_antes = pasos[idx - 2].distancias
                    visitados_antes = pasos[idx - 2].visitados

                paso = pasos[idx - 1]

                m1, m2, m3 = st.columns(3)
                m1.metric("Nodo procesado", paso.nodo_actual)
                m2.metric("Visitados", sum(paso.visitados))
                m3.metric("Iteración", f"{paso.iteracion} / {total_pasos}")

                with col_izq:
                    st.markdown(f"##### Iteración {paso.iteracion}")

                    candidatos = [
                        (v, distancias_antes[v]) for v in range(grafo.n) if not visitados_antes[v]
                    ]
                    st.caption("Vértices candidatos (no visitados) y su distancia tentativa:")
                    filas_candidatos = []
                    for v, dist in candidatos:
                        dist_str = "∞" if dist == INFINITO else str(dist)
                        filas_candidatos.append({
                            "Vértice": v,
                            "Distancia tentativa": dist_str,
                            "Seleccionado": "✓" if v == paso.nodo_actual else "",
                        })
                    st.table(filas_candidatos)
                    st.markdown(
                        f"➡️ Se elige el vértice **{paso.nodo_actual}** por tener la menor "
                        "distancia tentativa entre los candidatos no visitados."
                    )

                    if paso.actualizaciones:
                        st.caption("Actualizaciones de distancia en esta iteración:")
                        for vecino, anterior, nueva in paso.actualizaciones:
                            anterior_str = "∞" if anterior == INFINITO else anterior
                            st.write(f"- Vértice **{vecino}**: distancia {anterior_str} → **{nueva}**")
                    else:
                        st.caption("No hubo actualizaciones de distancia en esta iteración.")

                    with st.expander(f"📜 Historial completo (iteraciones 1 a {idx})"):
                        for p in pasos[:idx]:
                            detalle = (
                                ", ".join(f"{v}→{nueva}" for v, _, nueva in p.actualizaciones)
                                if p.actualizaciones else "sin actualizaciones"
                            )
                            st.write(f"**Iteración {p.iteracion}:** visita el vértice {p.nodo_actual}. ({detalle})")

                with col_der:
                    leyenda_grafo()
                    visitados_hasta_ahora = [v for v in range(grafo.n) if paso.visitados[v]]
                    dibujar_grafo(
                        grafo, layout, origen=origen, destino=destino,
                        actual=paso.nodo_actual, visitados=visitados_hasta_ahora,
                        distancias=paso.distancias, key=f"grafo_tab2_paso_{idx}",
                    )

                    tabla = []
                    for v in range(grafo.n):
                        dist_str = "∞" if paso.distancias[v] == INFINITO else str(paso.distancias[v])
                        tabla.append({
                            "Vértice": v,
                            "Distancia mínima": dist_str,
                            "Visitado": "✅" if paso.visitados[v] else "—",
                        })
                    st.table(tabla)

            if autoplay and idx < total_pasos:
                time.sleep(velocidad)
                st.session_state.paso_actual = idx + 1
                st.rerun()

            if idx == total_pasos and total_pasos > 0:
                st.success("✅ Ejecución completa. Revisa la pestaña **3. Solución** para ver el resultado final.")
        else:
            st.caption("Pulsa **Iniciar / reiniciar ejecución** para comenzar.")

# ---------------------------------------------------------------------------
# Pestaña 3: Solución
# ---------------------------------------------------------------------------

with tab_resultado:
    if st.session_state.pasos_dijkstra is None:
        st.info("Ejecuta el algoritmo en la pestaña **2** para ver la solución aquí.")
    else:
        distancias, predecesores, pasos = st.session_state.pasos_dijkstra
        total_pasos = len(pasos)
        if st.session_state.paso_actual < total_pasos:
            st.warning("La ejecución aún no ha terminado. Avanza hasta el último paso en la pestaña **2**.")
        elif distancias[destino] == INFINITO:
            st.error("El vértice destino no es alcanzable desde el origen.")
        else:
            caminos = reconstruir_caminos(predecesores, origen, destino)

            m1, m2, m3 = st.columns(3)
            m1.metric("Distancia mínima", distancias[destino])
            m2.metric("Caminos mínimos", len(caminos))
            m3.metric("Nodos totales", grafo.n)

            st.markdown("#### Caminos mínimos encontrados")
            for i, camino in enumerate(caminos, start=1):
                st.markdown(f"**Camino {i}:** " + " → ".join(
                    f"`{v}`" for v in camino
                ))

            aristas_resaltadas = []
            for camino in caminos:
                for a, b in zip(camino, camino[1:]):
                    aristas_resaltadas.append((a, b))

            st.markdown("#### Caminos mínimos resaltados sobre el grafo")
            st.caption("🔍 Puedes arrastrar el grafo o pasar el cursor sobre un vértice para ver su distancia.")
            leyenda_grafo()
            dibujar_grafo(
                grafo, layout, origen=origen, destino=destino,
                visitados=list(range(grafo.n)),
                aristas_resaltadas=aristas_resaltadas,
                distancias=distancias, key="grafo_tab3_resultado",
            )

            resumen = (
                f"Problema del camino mínimo - Algoritmo de Dijkstra\n"
                f"Vértice origen: {origen}\n"
                f"Vértice destino: {destino}\n"
                f"Distancia mínima: {distancias[destino]}\n"
                f"Cantidad de caminos mínimos: {len(caminos)}\n\n"
                + "\n".join(
                    f"Camino {i}: {' -> '.join(map(str, c))}"
                    for i, c in enumerate(caminos, start=1)
                )
            )
            st.download_button(
                "⬇️ Descargar resumen de resultados (.txt)",
                data=resumen,
                file_name="resultado_dijkstra.txt",
                mime="text/plain",
                type="primary",
            )