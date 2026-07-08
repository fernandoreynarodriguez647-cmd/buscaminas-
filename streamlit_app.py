import streamlit as st
from src.board import Board
from src.graph_builder import build_constraint_graph
from src.graph_analysis import obtener_componentes, particionar_tablero
from src.visualizer import dibujar_grafo


def inicializar_tablero(filas=9, columnas=9, minas=10):
    if 'tablero' not in st.session_state:
        tablero = Board(filas, columnas, minas)
        tablero.descubrir(filas // 2, columnas // 2)
        st.session_state.tablero = tablero


def reiniciar():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


st.set_page_config(page_title="Buscaminas Inteligente - Grafos", layout="wide")
st.title("Buscaminas Inteligente — Módulo de Grafos")

with st.sidebar:
    st.header("Configuración")
    filas = st.number_input("Filas", min_value=3, max_value=20, value=9)
    columnas = st.number_input("Columnas", min_value=3, max_value=20, value=9)
    minas = st.number_input("Minas", min_value=1, max_value=filas * columnas - 1, value=10)
    if st.button("Reiniciar tablero", type="primary"):
        reiniciar()
        st.rerun()

inicializar_tablero(filas, columnas, minas)
tablero = st.session_state.tablero

col_tablero, col_grafo = st.columns([1, 1])

with col_tablero:
    st.subheader("Tablero")
    celdas = []
    for f in range(tablero.filas):
        cols = st.columns(tablero.columnas)
        for c in range(tablero.columnas):
            estado = tablero.estado[f][c]
            if estado == 'descubierta':
                num = tablero.numeros[f][c]
                if num == 0:
                    label = "."
                else:
                    label = str(num)
                disabled = True
            elif estado == 'bandera':
                label = "F"
                disabled = True
            else:
                label = "?"
                disabled = False
            with cols[c]:
                if st.button(label, key=f"celda_{f}_{c}", disabled=disabled):
                    tablero.descubrir(f, c)
                    st.rerun()

with col_grafo:
    st.subheader("Grafo de restricciones")
    grafo = build_constraint_graph(tablero)
    subproblemas = particionar_tablero(tablero)
    componentes = [sp['nodos'] for sp in subproblemas]

    if grafo.number_of_nodes() > 0:
        fig = dibujar_grafo(grafo, componentes, mostrar=False)
        st.pyplot(fig)
    else:
        st.info("Aún no hay casillas frontera. Descubre más casillas en el tablero.")

col_metrics, col_detalle = st.columns([1, 1])

with col_metrics:
    st.subheader("Métricas")
    m1, m2, m3 = st.columns(3)
    m1.metric("Nodos", grafo.number_of_nodes())
    m2.metric("Aristas", grafo.number_of_edges())
    m3.metric("Componentes", len(componentes))

with col_detalle:
    st.subheader("Detalle de componentes")
    for i, sp in enumerate(subproblemas):
        with st.expander(f"Componente {i+1}: {len(sp['nodos'])} casillas"):
            st.write(f"**Casillas:** {sorted(sp['nodos'])}")
            st.write(f"**Restricciones:** {len(sp['restricciones'])}")
            for pos, restr in sp['restricciones'].items():
                st.write(f"  - ({pos[0]},{pos[1]}) → valor {restr['valor']}, vecinas {sorted(restr['vecinas_ocultas'])}")
