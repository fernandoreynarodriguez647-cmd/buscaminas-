import streamlit as st
import time
import json
import os
from datetime import datetime
from src.board import Board
from src.graph_builder import build_constraint_graph
from src.graph_analysis import obtener_componentes, particionar_tablero, metricas_grafo
from src.visualizer import dibujar_grafo, dibujar_grafo_comparativa
from src.solver_csp import BotJugador

DIFICULTADES = {
    'Principiante': {'filas': 9, 'columnas': 9, 'minas': 10},
    'Intermedio': {'filas': 16, 'columnas': 16, 'minas': 40},
    'Experto': {'filas': 16, 'columnas': 30, 'minas': 99},
    'Personalizado': {'filas': 9, 'columnas': 9, 'minas': 10},
}

HISTORIAL_FILE = 'historial_partidas.json'


def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def guardar_historial(historial):
    with open(HISTORIAL_FILE, 'w') as f:
        json.dump(historial, f, indent=2)


def agregar_partida(modo, dificultad, resultado, tiempo, filas, columnas, minas,
                     movidas_humano=0, movidas_bot=0, nodos_grafo=0, componentes=0):
    historial = cargar_historial()
    historial.append({
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'modo': modo,
        'dificultad': dificultad,
        'resultado': resultado,
        'tiempo': round(tiempo, 1),
        'filas': filas,
        'columnas': columnas,
        'minas': minas,
        'movidas_humano': movidas_humano,
        'movidas_bot': movidas_bot,
        'nodos_grafo': nodos_grafo,
        'componentes': componentes
    })
    guardar_historial(historial)


def inicializar_estado():
    if 'tablero' not in st.session_state:
        st.session_state.tablero = None
    if 'modo' not in st.session_state:
        st.session_state.modo = 'Practicar'
    if 'bot' not in st.session_state:
        st.session_state.bot = None
    if 'bot_tablero' not in st.session_state:
        st.session_state.bot_tablero = None
    if 'inicio' not in st.session_state:
        st.session_state.inicio = None
    if 'tiempo_humano' not in st.session_state:
        st.session_state.tiempo_humano = 0
    if 'tiempo_bot' not in st.session_state:
        st.session_state.tiempo_bot = 0
    if 'bot_jugando' not in st.session_state:
        st.session_state.bot_jugando = False
    if 'bot_termino' not in st.session_state:
        st.session_state.bot_termino = False
    if 'humano_termino' not in st.session_state:
        st.session_state.humano_termino = False
    if 'movidas_humano' not in st.session_state:
        st.session_state.movidas_humano = 0
    if 'movidas_bot' not in st.session_state:
        st.session_state.movidas_bot = 0
    if 'resultado' not in st.session_state:
        st.session_state.resultado = None
    if 'partida_guardada' not in st.session_state:
        st.session_state.partida_guardada = False


def crear_tablero(filas, columnas, minas):
    board = Board(filas, columnas, minas)
    board.descubrir(filas // 2, columnas // 2)
    return board


def reiniciar():
    for key in list(st.session_state.keys()):
        if key not in ['modo']:
            del st.session_state[key]
    inicializar_estado()


def obtener_estilo_casilla(estado, es_mina, game_over, numero, size):
    if game_over and es_mina and estado == 'oculta':
        return 'background-color: #E74C3C; color: white; font-weight: bold;'
    if estado == 'descubierta':
        if es_mina:
            return 'background-color: #C0392B; color: white; font-weight: bold;'
        colors = {0: '#ECF0F1', 1: '#3498DB', 2: '#27AE60', 3: '#E74C3C',
                  4: '#8E44AD', 5: '#D35400', 6: '#2C3E50', 7: '#7F8C8D', 8: '#95A5A6'}
        bg = colors.get(numero, '#ECF0F1')
        return f'background-color: {bg}; font-weight: bold;'
    if estado == 'bandera':
        return 'background-color: #F1C40F; color: black; font-weight: bold;'
    return 'background-color: #BDC3C7; font-weight: bold;'


def ejecutar_bot():
    if st.session_state.bot_tablero is None or st.session_state.bot_termino:
        return
    bot = BotJugador(st.session_state.bot_tablero)
    for _ in range(5):
        if st.session_state.bot_tablero.game_over or st.session_state.bot_tablero.won:
            break
        accion, pos = bot.jugar_turno()
        if pos:
            st.session_state.movidas_bot += 1
    if st.session_state.bot_tablero.game_over or st.session_state.bot_tablero.won:
        st.session_state.bot_termino = True
        st.session_state.tiempo_bot = time.time() - st.session_state.inicio
        verificar_resultado()


def verificar_resultado():
    if st.session_state.resultado is not None:
        return
    if st.session_state.modo == 'Practicar':
        if st.session_state.tablero.game_over:
            st.session_state.resultado = 'Derrota'
        elif st.session_state.tablero.won:
            st.session_state.resultado = 'Victoria'
    else:
        h_termino = st.session_state.tablero.won or st.session_state.tablero.game_over
        b_termino = st.session_state.bot_tablero.won or st.session_state.bot_tablero.game_over
        if h_termino and b_termino:
            if st.session_state.tablero.won and st.session_state.bot_tablero.won:
                if st.session_state.tiempo_humano < st.session_state.tiempo_bot:
                    st.session_state.resultado = 'Victoria (más rápido)'
                elif st.session_state.tiempo_humano > st.session_state.tiempo_bot:
                    st.session_state.resultado = 'Derrota (bot más rápido)'
                else:
                    st.session_state.resultado = 'Empate'
            elif st.session_state.tablero.won:
                st.session_state.resultado = 'Victoria'
            elif st.session_state.bot_tablero.won:
                st.session_state.resultado = 'Derrota'
            else:
                st.session_state.resultado = 'Ambos perdieron'
        elif h_termino:
            if st.session_state.tablero.won:
                st.session_state.resultado = 'Victoria'
                st.session_state.tiempo_humano = time.time() - st.session_state.inicio
            else:
                st.session_state.resultado = 'Derrota'
                st.session_state.tiempo_humano = time.time() - st.session_state.inicio


def pagina_inicio():
    st.title("Buscaminas Inteligente — Módulo de Grafos")
    st.markdown("""
    ### Entrena tu juego con ayuda de la teoría de grafos

    Este sistema modela el tablero de Buscaminas como un **grafo de restricciones**
    y lo divide en **componentes independientes** para resolverlo eficientemente.

    **Modos de juego:**
    - **Practicar** — Juega solo y observa el grafo en tiempo real
    - **Vs Bot** — Compite contra una IA basada en CSP
    - **Demo Bot** — Mira al bot resolver el tablero automáticamente
    """)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Practicar", use_container_width=True):
            st.session_state.modo = 'Practicar'
            reiniciar()
            st.rerun()
    with col2:
        if st.button("Vs Bot", use_container_width=True):
            st.session_state.modo = 'Vs Bot'
            reiniciar()
            st.rerun()
    with col3:
        if st.button("Demo Bot", use_container_width=True):
            st.session_state.modo = 'Demo Bot'
            reiniciar()
            st.rerun()
    st.divider()
    st.subheader("Estadísticas globales")
    hist = cargar_historial()
    if hist:
        total = len(hist)
        victorias = sum(1 for p in hist if 'Victoria' in p['resultado'])
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Partidas jugadas", total)
        col2.metric("Victorias", victorias)
        col3.metric("Derrotas", total - victorias)
        col4.metric("Win rate", f"{victorias / total * 100:.1f}%" if total else "0%")
    else:
        st.info("Aún no hay partidas registradas. ¡Juega una para ver tus estadísticas!")


def pagina_juego():
    dificultad = st.session_state.get('dificultad', 'Principiante')
    config = DIFICULTADES[dificultad]
    if dificultad == 'Personalizado':
        config['filas'] = st.session_state.get('cfg_filas', 9)
        config['columnas'] = st.session_state.get('cfg_columnas', 9)
        config['minas'] = st.session_state.get('cfg_minas', 10)
    filas, columnas, minas = config['filas'], config['columnas'], config['minas']

    if st.session_state.tablero is None:
        st.session_state.tablero = crear_tablero(filas, columnas, minas)
        st.session_state.inicio = time.time()
        st.session_state.partida_guardada = False
        if st.session_state.modo != 'Practicar':
            st.session_state.bot_tablero = crear_tablero(filas, columnas, minas)
            st.session_state.bot = BotJugador(st.session_state.bot_tablero)
            st.session_state.bot_termino = False
            st.session_state.bot_jugando = True
        st.session_state.humano_termino = False
        st.session_state.movidas_humano = 0
        st.session_state.movidas_bot = 0
        st.session_state.resultado = None
        st.session_state.tiempo_humano = 0
        st.session_state.tiempo_bot = 0

    tablero = st.session_state.tablero
    tocado = None
    bandera_toggle = None

    st.title(f"{st.session_state.modo} — {dificultad}")

    col_izq, col_der = st.columns([1, 1])

    with col_izq:
        if st.session_state.modo in ('Vs Bot', 'Demo Bot'):
            st.subheader("🧑 Humano")
            if st.session_state.modo == 'Demo Bot':
                st.caption("El bot juega automáticamente. Siéntate y observa.")
        else:
            st.subheader("🧑 Tu tablero")

        tiempo_actual = time.time() - st.session_state.inicio
        if not tablero.game_over and not tablero.won:
            st.session_state.tiempo_humano = tiempo_actual

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("⏱ Tiempo", f"{st.session_state.tiempo_humano:.1f}s")
        col_m2.metric("💣 Minas restantes", tablero.minas_restantes())
        col_m3.metric("🚩 Banderas", tablero.banderas_colocadas)

        max_size = max(filas, columnas)
        btn_size = max(30, min(60, 80 // max_size))

        if st.session_state.modo == 'Demo Bot':
            for f in range(filas):
                cols = st.columns(columnas)
                for c in range(columnas):
                    estado = tablero.estado[f][c]
                    if estado == 'descubierta':
                        num = tablero.numeros[f][c]
                        label = '.' if num == 0 else str(num)
                        disabled = True
                    elif estado == 'bandera':
                        label = '🚩'
                        disabled = True
                    elif tablero.game_over and tablero.minas[f][c]:
                        label = '💣'
                        disabled = True
                    else:
                        label = '?'
                        disabled = True
                    estilo = obtener_estilo_casilla(estado, tablero.minas[f][c],
                                                    tablero.game_over, tablero.numeros[f][c], btn_size)
                    with cols[c]:
                        st.button(label, key=f"h_{f}_{c}", disabled=disabled,
                                  use_container_width=True)
        else:
            for f in range(filas):
                cols = st.columns(columnas)
                for c in range(columnas):
                    estado = tablero.estado[f][c]
                    if estado == 'descubierta':
                        num = tablero.numeros[f][c]
                        label = '.' if num == 0 else str(num)
                        disabled = True
                    elif estado == 'bandera':
                        label = '🚩'
                        disabled = True
                    elif tablero.game_over and tablero.minas[f][c]:
                        label = '💣'
                        disabled = True
                    else:
                        label = '?'
                        disabled = False
                    with cols[c]:
                        if st.button(label, key=f"h_{f}_{c}", disabled=disabled,
                                     use_container_width=True):
                            if not tablero.game_over and not tablero.won:
                                if estado == 'oculta':
                                    tablero.descubrir(f, c)
                                    st.session_state.movidas_humano += 1
                                    st.rerun()

        if st.session_state.modo in ('Vs Bot', 'Demo Bot'):
            with col_der:
                st.subheader("🤖 Bot (CSP + AC-3)")
                bot_tablero = st.session_state.bot_tablero
                if bot_tablero:
                    col_b1, col_b2, col_b3 = st.columns(3)
                    col_b1.metric("⏱ Tiempo", f"{st.session_state.tiempo_bot:.1f}s")
                    col_b2.metric("💣 Minas restantes", bot_tablero.minas_restantes())
                    col_b3.metric("🔄 Movidas", st.session_state.movidas_bot)

                    for f in range(filas):
                        cols = st.columns(columnas)
                        for c in range(columnas):
                            estado = bot_tablero.estado[f][c]
                            if estado == 'descubierta':
                                num = bot_tablero.numeros[f][c]
                                label = '.' if num == 0 else str(num)
                            elif estado == 'bandera':
                                label = '🚩'
                            elif bot_tablero.game_over and bot_tablero.minas[f][c]:
                                label = '💣'
                            else:
                                label = '?'
                            with cols[c]:
                                st.button(label, key=f"b_{f}_{c}", disabled=True,
                                          use_container_width=True)

                    if st.session_state.modo == 'Vs Bot' and not st.session_state.bot_termino:
                        if st.button("🤖 Turno del Bot", use_container_width=True):
                            ejecutar_bot()
                            st.rerun()

                    if st.session_state.modo == 'Demo Bot' and not st.session_state.bot_termino:
                        ejecutar_bot()
                        time.sleep(0.3)
                        st.rerun()

    if tablero.game_over:
        for f in range(filas):
            for c in range(columnas):
                if tablero.minas[f][c] and tablero.estado[f][c] != 'bandera':
                    tablero.estado[f][c] = 'descubierta'

    if tablero.game_over or tablero.won:
        if not st.session_state.humano_termino:
            st.session_state.humano_termino = True
            st.session_state.tiempo_humano = time.time() - st.session_state.inicio
            verificar_resultado()

    if st.session_state.resultado:
        r = st.session_state.resultado
        if 'Victoria' in r:
            st.balloons()
            st.success(f"### 🎉 {r}!")
        elif 'Derrota' in r or 'perdieron' in r:
            st.error(f"### 💥 {r}")
        else:
            st.info(f"### 🤝 {r}")

        g_h = build_constraint_graph(st.session_state.tablero)
        met_h = metricas_grafo(g_h)
        g_b = None
        met_b = None
        if st.session_state.bot_tablero:
            g_b = build_constraint_graph(st.session_state.bot_tablero)
            met_b = metricas_grafo(g_b)

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Tiempo humano", f"{st.session_state.tiempo_humano:.1f}s")
        if st.session_state.modo != 'Practicar':
            col_r2.metric("Tiempo bot", f"{st.session_state.tiempo_bot:.1f}s")
            diff = st.session_state.tiempo_humano - st.session_state.tiempo_bot
            col_r3.metric("Diferencia", f"{'+' if diff > 0 else ''}{diff:.1f}s")
        else:
            col_r2.metric("Nodos del grafo", met_h['nodos'])
            col_r3.metric("Componentes", met_h['componentes'])

        st.subheader("📊 Comparativa de grafos finales")
        if st.session_state.bot_tablero:
            comps_h = obtener_componentes(g_h)
            comps_b = obtener_componentes(g_b)
            fig = dibujar_grafo_comparativa(g_h, comps_h, g_b, comps_b)
            st.pyplot(fig)
        else:
            comps_h = obtener_componentes(g_h)
            fig = dibujar_grafo(g_h, comps_h, mostrar=False)
            st.pyplot(fig)

        if st.button("🔄 Nueva partida", use_container_width=True):
            if not st.session_state.partida_guardada:
                agregar_partida(
                    modo=st.session_state.modo,
                    dificultad=dificultad,
                    resultado=st.session_state.resultado,
                    tiempo=st.session_state.tiempo_humano,
                    filas=filas, columnas=columnas, minas=minas,
                    movidas_humano=st.session_state.movidas_humano,
                    movidas_bot=st.session_state.movidas_bot if st.session_state.modo != 'Practicar' else 0,
                    nodos_grafo=met_h['nodos'],
                    componentes=met_h['componentes']
                )
                st.session_state.partida_guardada = True
            reiniciar()
            st.rerun()

    else:
        st.divider()
        col_g, col_m = st.columns([2, 1])

        with col_g:
            st.subheader("📈 Grafo de restricciones")
            grafo = build_constraint_graph(tablero)
            subproblemas = particionar_tablero(tablero)
            componentes = [sp['nodos'] for sp in subproblemas]
            if grafo.number_of_nodes() > 0:
                fig = dibujar_grafo(grafo, componentes, mostrar=False)
                st.pyplot(fig)
            else:
                st.info("Aún no hay casillas frontera. Descubre más casillas.")

        with col_m:
            st.subheader("📊 Métricas del grafo")
            met = metricas_grafo(grafo)
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Nodos", met['nodos'])
            col_m2.metric("Aristas", met['aristas'])
            col_m1.metric("Componentes", met['componentes'])
            col_m2.metric("Comp. más grande", met['componente_mas_grande'])
            col_m1.metric("Densidad", f"{met['densidad']:.3f}")
            col_m2.metric("Grado promedio", f"{met['grado_promedio']:.2f}")

            with st.expander("🔍 Detalle de componentes"):
                for i, sp in enumerate(subproblemas):
                    st.markdown(f"**Componente {i+1}:** {len(sp['nodos'])} casillas, "
                                f"{len(sp['restricciones'])} restricciones")
                    st.write(f"Nodos: {sorted(sp['nodos'])}")
                    for pos, restr in sp['restricciones'].items():
                        st.write(f"  ({pos[0]},{pos[1]}) → {restr['valor']}, "
                                 f"vecinas: {sorted(restr['vecinas_ocultas'])}")

    with st.sidebar:
        st.header("⚙️ Configuración")
        dificultad = st.selectbox(
            "Dificultad", list(DIFICULTADES.keys()),
            key='dificultad',
            on_change=lambda: reiniciar()
        )
        if dificultad == 'Personalizado':
            cfg_filas = st.number_input("Filas", 3, 20, 9, key='cfg_filas')
            cfg_cols = st.number_input("Columnas", 3, 20, 9, key='cfg_columnas')
            max_minas = cfg_filas * cfg_cols - 1
            st.number_input("Minas", 1, max_minas, 10, key='cfg_minas')
        if st.button("🔄 Reiniciar partida", type="primary", use_container_width=True):
            reiniciar()
            st.rerun()
        st.divider()
        st.subheader("📋 Historial")
        hist = cargar_historial()
        if hist:
            for p in hist[-5:][::-1]:
                emoji = '✅' if 'Victoria' in p['resultado'] else '❌'
                st.markdown(f"{emoji} **{p['modo']}** — {p['dificultad']}")
                st.caption(f"{p['resultado']} | {p['tiempo']}s | {p['fecha'][:10]}")
        else:
            st.caption("Sin partidas aún")

        if hist:
            st.divider()
            total = len(hist)
            wins = sum(1 for p in hist if 'Victoria' in p['resultado'])
            st.metric("Win rate global", f"{wins / total * 100:.1f}%" if total else "0%")
            st.download_button(
                "📥 Exportar historial",
                data=json.dumps(hist, indent=2),
                file_name='historial_partidas.json',
                mime='application/json'
            )


def pagina_historial():
    st.title("📋 Historial de partidas")
    hist = cargar_historial()
    if not hist:
        st.info("No hay partidas registradas aún.")
        return
    total = len(hist)
    wins = sum(1 for p in hist if 'Victoria' in p['resultado'])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", total)
    col2.metric("Victorias", wins)
    col3.metric("Derrotas", total - wins)
    col4.metric("Win rate", f"{wins / total * 100:.1f}%")
    st.divider()
    for p in reversed(hist):
        emoji = '✅' if 'Victoria' in p['resultado'] else '❌'
        with st.expander(f"{emoji} {p['modo']} — {p['dificultad']} — {p['fecha']}"):
            st.json(p)
    if st.button("🗑️ Limpiar historial"):
        guardar_historial([])
        st.rerun()


def main():
    inicializar_estado()
    st.set_page_config(page_title="Buscaminas Inteligente - Grafos", layout="wide",
                       page_icon="💣")

    if st.session_state.tablero is not None:
        pagina_juego()
    elif 'pagina' in st.session_state and st.session_state.pagina == 'historial':
        pagina_historial()
    else:
        pagina_inicio()


if __name__ == '__main__':
    main()
