import streamlit as st
import time
import json
import os
from datetime import datetime
from src.board import Board
from src.graph_builder import build_constraint_graph
from src.graph_analysis import obtener_componentes, particionar_tablero, metricas_grafo
from src.visualizer import dibujar_grafo
from src.solver_csp import BotJugador

st.set_page_config(page_title="Buscaminas Inteligente - Grafos", layout="wide", page_icon="💣")

DIFICULTADES = {
    'Principiante': {'filas': 9, 'columnas': 9, 'minas': 10},
    'Intermedio': {'filas': 16, 'columnas': 16, 'minas': 40},
    'Experto': {'filas': 16, 'columnas': 30, 'minas': 99},
    'Personalizado': {'filas': 9, 'columnas': 9, 'minas': 10},
}

HISTORIAL_FILE = 'historial_partidas.json'

# ─── GAMER COLOR SCHEME ───
C_NEON = {
    'bg': '#0E1117',
    'card': '#1A1D2E',
    'accent': '#00FF88',
    'accent2': '#FF6B35',
    'accent3': '#00D4FF',
    'bronze': '#CD7F32',
    'silver': '#C0C0C0',
    'gold': '#FFD700',
    'danger': '#FF3366',
    'success': '#00FF88',
    'text': '#E0E0E0',
    'muted': '#6B7280',
}

RANKOS = {
    'Bronce': {'icon': '🥉', 'color': C_NEON['bronze'], 'min_winrate': 0, 'min_juegos': 1},
    'Plata': {'icon': '🥈', 'color': C_NEON['silver'], 'min_winrate': 45, 'min_juegos': 5},
    'Oro': {'icon': '🥇', 'color': C_NEON['gold'], 'min_winrate': 70, 'min_juegos': 15},
}


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


def calcular_rango(historial):
    if not historial:
        return 'Bronce', 0
    total = len(historial)
    wins = sum(1 for p in historial if 'Victoria' in p['resultado'])
    winrate = wins / total * 100 if total > 0 else 0
    for rango, req in reversed(list(RANKOS.items())):
        if total >= req['min_juegos'] and winrate >= req['min_winrate']:
            return rango, winrate
    return 'Bronce', winrate


def calcular_mejores_tiempos(historial):
    tiempos = {}
    for p in historial:
        if 'Victoria' in p['resultado']:
            dif = p.get('dificultad', 'Desconocida')
            t = p.get('tiempo', 999)
            if dif not in tiempos or t < tiempos[dif]['mejor']:
                tiempos[dif] = {
                    'mejor': t,
                    'ultimo': t,
                    'total': t,
                    'count': 1
                }
            else:
                tiempos[dif]['ultimo'] = t
                tiempos[dif]['total'] += t
                tiempos[dif]['count'] += 1
    for dif in tiempos:
        tiempos[dif]['promedio'] = round(tiempos[dif]['total'] / tiempos[dif]['count'], 1)
    return tiempos


def inicializar_estado():
    for key, default in [
        ('tablero', None), ('modo', 'Practicar'),
        ('bot_tablero', None), ('inicio', None), ('tiempo_humano', 0),
        ('tiempo_bot', 0), ('bot_jugando', False), ('bot_termino', False),
        ('humano_termino', False), ('movidas_humano', 0), ('movidas_bot', 0),
        ('resultado', None), ('partida_guardada', False), ('pagina_activa', 'Inicio'),
        ('dificultad', 'Principiante'), ('modo_bandera', False),
        ('bot_explicacion', ''), ('bot_empezo', False), ('partida_iniciada', False),
        ('bot_ultima_pos', None), ('bot_automatico', False), ('bot_ultimo_tiempo', 0.0),
        ('vs_iniciado', False), ('bot_velocidad', 0.8)
    ]:
        if key not in st.session_state:
            st.session_state[key] = default


def crear_tablero(filas, columnas, minas):
    while True:
        board = Board(filas, columnas, minas)
        board.descubrir(filas // 2, columnas // 2)
        if not board.game_over:
            return board


def crear_tableros_iguales(filas, columnas, minas):
    while True:
        board = Board(filas, columnas, minas)
        board.descubrir(filas // 2, columnas // 2)
        if not board.game_over:
            break
    posiciones_minas = [(f, c) for f in range(filas) for c in range(columnas) if board.minas[f][c]]
    board2 = Board(filas, columnas, minas, minas_predefinidas=posiciones_minas)
    board2.descubrir(filas // 2, columnas // 2)
    return board, board2


def reiniciar():
    keep = ['modo', 'pagina_activa', 'dificultad', 'modo_bandera', 'bot_explicacion',
            'cfg_filas', 'cfg_columnas', 'cfg_minas']
    keys = list(st.session_state.keys())
    for k in keys:
        if k not in keep:
            del st.session_state[k]
    inicializar_estado()


def iniciar_partida():
    dif = st.session_state.dificultad
    cfg = dict(DIFICULTADES[dif])
    if dif == 'Personalizado':
        cfg['filas'] = st.session_state.get('cfg_filas', 9)
        cfg['columnas'] = st.session_state.get('cfg_columnas', 9)
        cfg['minas'] = st.session_state.get('cfg_minas', 10)
    filas, columnas, minas = cfg['filas'], cfg['columnas'], cfg['minas']
    modo = st.session_state.modo
    st.session_state.inicio = time.time()
    st.session_state.partida_guardada = False
    st.session_state.humano_termino = False
    st.session_state.movidas_humano = 0
    st.session_state.movidas_bot = 0
    st.session_state.resultado = None
    st.session_state.tiempo_humano = 0
    st.session_state.tiempo_bot = 0
    st.session_state.bot_termino = False
    st.session_state.partida_iniciada = True
    if modo == 'Demo Bot':
        st.session_state.tablero = None
        st.session_state.bot_tablero = crear_tablero(filas, columnas, minas)
        st.session_state.bot_empezo = False
    elif modo == 'Practicar':
        st.session_state.tablero = crear_tablero(filas, columnas, minas)
    else:
        t1, t2 = crear_tableros_iguales(filas, columnas, minas)
        st.session_state.tablero = t1
        st.session_state.bot_tablero = t2
        st.session_state.vs_iniciado = False


def ejecutar_bot(un_paso=False):
    if st.session_state.bot_termino:
        return
    tablero_bot = st.session_state.bot_tablero
    if tablero_bot is None or tablero_bot.game_over or tablero_bot.won:
        st.session_state.bot_termino = True
        st.session_state.tiempo_bot = time.time() - st.session_state.inicio
        verificar_resultado()
        return
    bot = BotJugador(tablero_bot)
    pasos = 1 if un_paso else 3
    for _ in range(pasos):
        if tablero_bot.game_over or tablero_bot.won:
            break
        accion, pos, explicacion = bot.jugar_turno()
        if pos:
            st.session_state.movidas_bot += 1
            st.session_state.bot_explicacion = explicacion
            st.session_state.bot_ultima_pos = pos
    if tablero_bot.game_over or tablero_bot.won:
        st.session_state.bot_termino = True
        st.session_state.tiempo_bot = time.time() - st.session_state.inicio
        verificar_resultado()
    if st.session_state.modo == 'Demo Bot' and not st.session_state.bot_termino:
        st.session_state.tiempo_bot = time.time() - st.session_state.inicio


def verificar_resultado():
    if st.session_state.resultado is not None:
        return
    t = st.session_state.tablero
    if st.session_state.modo == 'Practicar':
        if t.game_over:
            st.session_state.resultado = 'Derrota'
        elif t.won:
            st.session_state.resultado = 'Victoria'
        return
    if st.session_state.modo == 'Demo Bot':
        b = st.session_state.bot_tablero
        if b.won:
            st.session_state.resultado = 'Victoria'
        elif b.game_over:
            st.session_state.resultado = 'Derrota'
        return
    h = t
    b = st.session_state.bot_tablero
    h_term = h.won or h.game_over
    b_term = b.won or b.game_over
    if h_term and b_term:
        if h.won and b.won:
            ht = st.session_state.tiempo_humano
            bt_t = st.session_state.tiempo_bot
            st.session_state.resultado = 'Victoria (más rápido)' if ht < bt_t else 'Derrota (bot más rápido)' if ht > bt_t else 'Empate'
        elif h.won:
            st.session_state.resultado = 'Victoria'
        elif b.won:
            st.session_state.resultado = 'Derrota'
        else:
            st.session_state.resultado = 'Ambos perdieron'
    elif h_term:
        st.session_state.resultado = 'Victoria' if h.won else 'Derrota'
    elif b_term:
        st.session_state.resultado = 'Derrota' if b.won else 'Victoria'


# ─── COMPONENTES UI ───

def css_gamer():
    st.markdown(f"""
    <style>
        .stApp {{ background: {C_NEON['bg']}; color: {C_NEON['text']}; }}
        .stButton>button {{ background: {C_NEON['card']}; color: {C_NEON['text']}; border: 1px solid {C_NEON['accent']}; border-radius: 8px; }}
        .stButton>button:hover {{ border-color: {C_NEON['accent2']}; box-shadow: 0 0 15px {C_NEON['accent2']}40; }}
        .flag-mode-active button {{ background: {C_NEON['accent2']}33 !important; border-color: {C_NEON['accent2']} !important; }}
        .flag-mode-inactive button {{ border-color: {C_NEON['accent']} !important; }}
        div[data-testid="stMetricValue"] {{ color: {C_NEON['accent']} !important; font-size: 1.8rem !important; }}
        div[data-testid="stMetricLabel"] {{ color: {C_NEON['muted']} !important; }}
        .rank-badge {{ font-size: 2rem; padding: 10px 25px; border-radius: 15px; text-align: center; font-weight: bold; display: inline-block; }}
        .card {{ background: {C_NEON['card']}; border-radius: 12px; padding: 20px; border: 1px solid {C_NEON['muted']}33; margin: 10px 0; }}
        .card h3 {{ color: {C_NEON['accent3']}; margin-top: 0; }}
        .stat-number {{ color: {C_NEON['accent']}; font-size: 2.2rem; font-weight: bold; }}
        .stat-label {{ color: {C_NEON['muted']}; font-size: 0.85rem; }}
        .mejor-tiempo {{ color: {C_NEON['gold']}; font-size: 1.6rem; font-weight: bold; }}
        hr {{ border-color: {C_NEON['muted']}44; }}
        .stTabs [data-baseweb="tab-list"] {{ gap: 2px; }}
        .stTabs [data-baseweb="tab"] {{ background: {C_NEON['card']}; color: {C_NEON['text']}; border-radius: 8px 8px 0 0 !important; }}
        .stTabs [aria-selected="true"] {{ background: {C_NEON['accent']}22 !important; border-bottom: 2px solid {C_NEON['accent']} !important; }}
        .stExpander {{ background: {C_NEON['card']}; border-radius: 10px; border: 1px solid {C_NEON['muted']}33; }}
        @keyframes destello {{ 0% {{ box-shadow: 0 0 15px {C_NEON['gold']}; }} 100% {{ box-shadow: 0 0 0px transparent; }} }}
    </style>
    """, unsafe_allow_html=True)


def render_rank_badge(rango, winrate):
    info = RANKOS[rango]
    st.markdown(f"""
    <div class="rank-badge" style="background: linear-gradient(135deg, {C_NEON['card']}, {info['color']}22); border: 2px solid {info['color']};">
        <span style="font-size:3rem;">{info['icon']}</span><br>
        <span style="color:{info['color']};">{rango.upper()}</span><br>
        <span style="color:{C_NEON['muted']};font-size:1rem;">Win Rate: {winrate:.1f}%</span>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card(titulo, valor, unidad=''):
    st.markdown(f"""
    <div class="card">
        <div class="stat-label">{titulo}</div>
        <div class="stat-number">{valor}</div>
        <div class="stat-label">{unidad}</div>
    </div>
    """, unsafe_allow_html=True)


def pagina_perfil():
    col_tit, col_volver = st.columns([5, 1])
    with col_tit:
        st.title("🏆 Perfil del Jugador")
    with col_volver:
        if st.button("← Inicio", use_container_width=True):
            st.session_state.pagina_activa = 'Inicio'
            st.rerun()
    hist = cargar_historial()
    if not hist:
        st.info("Aún no hay partidas registradas. ¡Juega para generar estadísticas!")
        return
    rango, winrate = calcular_rango(hist)
    total = len(hist)
    wins = sum(1 for p in hist if 'Victoria' in p['resultado'])
    losses = total - wins
    tiempos = calcular_mejores_tiempos(hist)

    col_badge, col_stats = st.columns([1, 2])
    with col_badge:
        render_rank_badge(rango, winrate)
    with col_stats:
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='card'><div class='stat-label'>Partidas</div><div class='stat-number'>{total}</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><div class='stat-label'>Victorias</div><div class='stat-number' style='color:{C_NEON['success']}'>{wins}</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><div class='stat-label'>Derrotas</div><div class='stat-number' style='color:{C_NEON['danger']}'>{losses}</div></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='card'><div class='stat-label'>Win Rate</div><div class='stat-number'>{winrate:.1f}%</div></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("⏱ Mejores Tiempos por Dificultad")
    if tiempos:
        cols = st.columns(len(tiempos))
        for i, (dif, data) in enumerate(sorted(tiempos.items())):
            with cols[i]:
                st.markdown(f"""
                <div class="card" style="text-align:center;">
                    <div class="stat-label">{dif}</div>
                    <div class="mejor-tiempo">⏱ {data['mejor']:.1f}s</div>
                    <div class="stat-label">Mejor tiempo</div>
                    <div style="color:{C_NEON['accent3']};margin-top:10px;">Promedio: {data['promedio']:.1f}s</div>
                    <div style="color:{C_NEON['muted']};">Último: {data['ultimo']:.1f}s</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Aún no tienes victorias registradas. ¡Gana partidas para ver tus tiempos!")

    st.divider()
    st.subheader("📜 Progreso hacia el siguiente rango")
    rank_order = ['Bronce', 'Plata', 'Oro']
    idx_actual = rank_order.index(rango)
    for i, r in enumerate(rank_order):
        req = RANKOS[r]
        unlocked = i <= idx_actual
        emoji = '🔓' if unlocked else '🔒'
        color = req['color'] if unlocked else C_NEON['muted']
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:15px;padding:10px;background:{C_NEON['card']};border-radius:10px;margin:5px 0;border-left:4px solid {color};opacity:{1.0 if unlocked else 0.5};">
            <span style="font-size:2rem;">{emoji}</span>
            <div>
                <strong style="color:{color};font-size:1.2rem;">{req['icon']} {r}</strong><br>
                <span style="color:{C_NEON['muted']};">Win Rate ≥ {req['min_winrate']}% · Mín. {req['min_juegos']} partidas</span>
            </div>
            <div style="margin-left:auto;text-align:right;">
                <span style="color:{color};font-size:1.4rem;">{'✅' if unlocked else '❌'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    with st.expander("📋 Historial completo de partidas"):
        for p in reversed(hist):
            emoji = '✅' if 'Victoria' in p['resultado'] else '❌'
            st.markdown(f"{emoji} **{p['modo']}** — {p['dificultad']} — {p['resultado']} — ⏱ {p['tiempo']}s — {p['fecha']}")


def pagina_tiempos():
    col_tit, col_volver = st.columns([5, 1])
    with col_tit:
        st.title("⏱ Récords de Tiempo")
    with col_volver:
        if st.button("← Inicio", use_container_width=True):
            st.session_state.pagina_activa = 'Inicio'
            st.rerun()
    hist = cargar_historial()
    if not hist:
        st.info("No hay partidas registradas. ¡Juega para establecer récords!")
        return
    tiempos = calcular_mejores_tiempos(hist)
    victorias = [p for p in hist if 'Victoria' in p['resultado']]
    st.subheader("🏅 Podio de mejores tiempos")
    if victorias:
        mejores = sorted(victorias, key=lambda x: x['tiempo'])[:10]
        cols = st.columns(3)
        medallas = ['🥇', '🥈', '🥉']
        for i, p in enumerate(mejores[:3]):
            with cols[i]:
                st.markdown(f"""
                <div class="card" style="text-align:center;border:2px solid {C_NEON['gold'] if i==0 else C_NEON['silver'] if i==1 else C_NEON['bronze']};">
                    <div style="font-size:3rem;">{medallas[i]}</div>
                    <div class="mejor-tiempo">{p['tiempo']:.1f}s</div>
                    <div class="stat-label">{p['dificultad']} · {p['modo']} · {p['fecha'][:10]}</div>
                </div>
                """, unsafe_allow_html=True)
        st.divider()
        st.subheader("📊 Top 10 mejores tiempos")
        data = []
        for i, p in enumerate(mejores):
            data.append([i+1, p['dificultad'], p['modo'], f"{p['tiempo']:.1f}s", p['fecha'][:10]])
        st.table(data)
    else:
        st.info("Aún no hay victorias. ¡Gana partidas para aparecer en el podio!")


def pagina_juego():
    dificultad = st.session_state.dificultad
    config = DIFICULTADES[dificultad]
    if dificultad == 'Personalizado':
        config['filas'] = st.session_state.get('cfg_filas', 9)
        config['columnas'] = st.session_state.get('cfg_columnas', 9)
        config['minas'] = st.session_state.get('cfg_minas', 10)
    filas, columnas, minas = config['filas'], config['columnas'], config['minas']

    if not st.session_state.partida_iniciada:
        st.title("🎮 Jugar")
        st.markdown(f"""
        <div class="card" style="text-align:center;border:2px solid {C_NEON['accent']};">
            <h3 style="color:{C_NEON['accent']};">Selecciona un modo de juego</h3>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🎮 Practicar", use_container_width=True):
                st.session_state.modo = 'Practicar'
                iniciar_partida()
                st.rerun()
        with c2:
            if st.button("🤖 Vs Bot", use_container_width=True):
                st.session_state.modo = 'Vs Bot'
                iniciar_partida()
                st.rerun()
        with c3:
            if st.button("👀 Demo Bot", use_container_width=True):
                st.session_state.modo = 'Demo Bot'
                iniciar_partida()
                st.rerun()
        st.info("Elige un modo para comenzar. Usa el menú lateral para configurar la dificultad.")
        return

    tablero = st.session_state.tablero
    es_vs_bot = st.session_state.modo == 'Vs Bot'

    col_tit, col_volver = st.columns([5, 1])
    with col_tit:
        st.title(f"🎮 {st.session_state.modo} — {dificultad}")
    with col_volver:
        if st.button("← Volver", use_container_width=True):
            reiniciar()
            st.session_state.partida_iniciada = False
            st.rerun()

    tab_juego, tab_grafo, tab_detalle = st.tabs(["🎯 Partida", "📈 Grafo", "🔍 Detalle"])

    with tab_juego:
        if st.session_state.modo == 'Demo Bot':
            bt = st.session_state.bot_tablero
            st.subheader("🤖 Bot resolviendo paso a paso")
            col1, col2, col3 = st.columns(3)
            col1.metric("⏱ Tiempo", f"{st.session_state.tiempo_bot:.1f}s")
            col2.metric("💣 Minas rest.", bt.minas_restantes())
            col3.metric("🔄 Movidas", st.session_state.movidas_bot)

            col_tablero, col_explicacion = st.columns([2, 1])
            with col_tablero:
                ult_f, ult_c = st.session_state.bot_ultima_pos or (None, None)
                for f in range(filas):
                    cols = st.columns(columnas)
                    for c in range(columnas):
                        e = bt.estado[f][c]
                        es_ultima = (f == ult_f and c == ult_c)
                        if e == 'descubierta':
                            n = bt.numeros[f][c]
                            lbl = '.' if n == 0 else str(n)
                            if es_ultima:
                                lbl = f'**{lbl}**'
                        elif e == 'bandera':
                            lbl = '🚩'
                            if es_ultima:
                                lbl = '⛳'
                        elif bt.game_over and bt.minas[f][c]:
                            lbl = '💣'
                        else:
                            lbl = '?'
                        with cols[c]:
                            style = ''
                            if es_ultima:
                                style = f'background:{C_NEON["accent"]}44;border:2px solid {C_NEON["accent"]}!important;font-weight:bold;'
                            st.markdown(
                                f'<div style="text-align:center;padding:5px 0;border-radius:4px;'
                                f'background:{C_NEON["card"]};border:1px solid {C_NEON["muted"]}55;{style}">'
                                f'{lbl}</div>',
                                unsafe_allow_html=True
                            )

            with col_explicacion:
                st.markdown("### 🧠 Explicación")
                if st.session_state.bot_explicacion:
                    st.info(st.session_state.bot_explicacion)
                else:
                    st.caption("Presiona 'Paso a paso' para ver el primer movimiento del bot.")

            if not st.session_state.bot_empezo:
                if st.button("▶️ Iniciar Bot — Paso a paso", type="primary", use_container_width=True):
                    st.session_state.bot_empezo = True
                    st.rerun()
            elif not st.session_state.bot_termino:
                if st.button("⏭ Siguiente paso", use_container_width=True):
                    ejecutar_bot(un_paso=True)
                    st.rerun()
            if st.session_state.bot_termino:
                st.success("✅ El bot completó el análisis del tablero.")

        elif st.session_state.modo == 'Vs Bot':
            bt = st.session_state.bot_tablero
            if not st.session_state.vs_iniciado:
                st.subheader("🏁 Vs Bot — Listo para competir")
                st.markdown("**Cada jugador tiene su propio tablero** con distinta distribución de minas. "
                           "El primero en resolver su tablero gana.")
                vel = st.slider("⏱ Velocidad del bot (segundos entre movimientos)",
                                0.2, 2.0, float(st.session_state.bot_velocidad), 0.1)
                st.session_state.bot_velocidad = vel
                st.markdown(f"<div style='text-align:center;font-size:1.2rem;'>⏱ El bot hará un movimiento cada <b>{vel:.1f}s</b></div>",
                           unsafe_allow_html=True)
                if st.button("▶️ Iniciar partida", type="primary", use_container_width=True):
                    st.session_state.inicio = time.time()
                    st.session_state.tiempo_humano = 0
                    st.session_state.tiempo_bot = 0
                    st.session_state.movidas_humano = 0
                    st.session_state.movidas_bot = 0
                    st.session_state.bot_termino = False
                    st.session_state.humano_termino = False
                    st.session_state.resultado = None
                    st.session_state.vs_iniciado = True
                    st.session_state.bot_ultimo_tiempo = time.time()
                    st.rerun()
            else:
                tiempo_actual = time.time() - st.session_state.inicio
                if not tablero.game_over and not tablero.won:
                    st.session_state.tiempo_humano = tiempo_actual
                if not bt.game_over and not bt.won:
                    st.session_state.tiempo_bot = tiempo_actual

                col_hum, col_bot = st.columns(2)
                with col_hum:
                    st.subheader("🧑 Humano")
                    hm1, hm2, hm3 = st.columns(3)
                    hm1.metric("⏱ Tiempo", f"{st.session_state.tiempo_humano:.1f}s")
                    hm2.metric("💣 Minas rest.", tablero.minas_restantes())
                    hm3.metric("🚩 Banderas", tablero.banderas_colocadas)

                    modo_bandera = st.session_state.modo_bandera
                    icon = '🚩' if not modo_bandera else '🔍'
                    if st.button(f"{icon} {'Marcar bandera' if not modo_bandera else 'Descubrir'}",
                                 use_container_width=True):
                        st.session_state.modo_bandera = not modo_bandera
                        st.rerun()

                    for f in range(filas):
                        cols = st.columns(columnas)
                        for c in range(columnas):
                            estado = tablero.estado[f][c]
                            disabled = True
                            if estado == 'descubierta':
                                num = tablero.numeros[f][c]
                                label = '.' if num == 0 else str(num)
                            elif estado == 'bandera':
                                label = '🚩'
                            elif tablero.game_over and tablero.minas[f][c]:
                                label = '💣'
                            else:
                                label = '🚩' if modo_bandera else '?'
                                disabled = False
                            with cols[c]:
                                if st.button(label, key=f"h_{f}_{c}", disabled=disabled,
                                             use_container_width=True):
                                    if not tablero.game_over and not tablero.won:
                                        if modo_bandera and estado == 'oculta':
                                            tablero.marcar_bandera(f, c)
                                            st.rerun()
                                        elif not modo_bandera and estado == 'oculta':
                                            tablero.descubrir(f, c)
                                            st.session_state.movidas_humano += 1
                                            if tablero.game_over or tablero.won:
                                                st.session_state.tiempo_humano = time.time() - st.session_state.inicio
                                                verificar_resultado()
                                            st.rerun()

                with col_bot:
                    st.subheader("🤖 Bot")
                    bm1, bm2, bm3 = st.columns(3)
                    bm1.metric("⏱ Tiempo", f"{st.session_state.tiempo_bot:.1f}s")
                    bm2.metric("💣 Minas rest.", bt.minas_restantes())
                    bm3.metric("🔄 Movidas", st.session_state.movidas_bot)
                    if st.session_state.bot_explicacion:
                        st.caption(st.session_state.bot_explicacion)

                    ult_f, ult_c = st.session_state.bot_ultima_pos or (None, None)
                    for f in range(filas):
                        cols = st.columns(columnas)
                        for c in range(columnas):
                            e = bt.estado[f][c]
                            es_ultima = (f == ult_f and c == ult_c)
                            if e == 'descubierta':
                                n = bt.numeros[f][c]
                                lbl = '.' if n == 0 else str(n)
                                if es_ultima:
                                    lbl = f'**{lbl}**'
                            elif e == 'bandera':
                                lbl = '🚩'
                                if es_ultima:
                                    lbl = '⛳'
                            elif bt.game_over and bt.minas[f][c]:
                                lbl = '💣'
                            else:
                                lbl = '?'
                            with cols[c]:
                                style = ''
                                if es_ultima:
                                    style = f'background:{C_NEON["gold"]}55;border:2px solid {C_NEON["gold"]}!important;font-weight:bold;animation:destello 0.5s ease;'
                                st.markdown(
                                    f'<div style="text-align:center;padding:5px 0;border-radius:4px;'
                                    f'background:{C_NEON["card"]};border:1px solid {C_NEON["muted"]}55;{style}">'
                                    f'{lbl}</div>',
                                    unsafe_allow_html=True
                                )

                    if not st.session_state.bot_termino:
                        vel = st.session_state.bot_velocidad
                        ahora = time.time()
                        if ahora - st.session_state.bot_ultimo_tiempo >= vel:
                            ejecutar_bot(un_paso=True)
                            st.session_state.bot_ultimo_tiempo = time.time()
                            time.sleep(0.15)
                            st.rerun()
                    else:
                        st.caption("✅ Bot terminó")

        else:
            st.subheader("🧑 Practicar")
            tiempo_actual = time.time() - st.session_state.inicio
            if not tablero.game_over and not tablero.won:
                st.session_state.tiempo_humano = tiempo_actual
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("⏱ Tiempo", f"{st.session_state.tiempo_humano:.1f}s")
            mc2.metric("💣 Minas rest.", tablero.minas_restantes())
            mc3.metric("🚩 Banderas", tablero.banderas_colocadas)

            modo_bandera = st.session_state.modo_bandera
            icon = '🚩' if not modo_bandera else '🔍'
            if st.button(f"{icon} {'Marcar bandera' if not modo_bandera else 'Descubrir'}", use_container_width=True):
                st.session_state.modo_bandera = not modo_bandera
                st.rerun()

            for f in range(filas):
                cols = st.columns(columnas)
                for c in range(columnas):
                    estado = tablero.estado[f][c]
                    disabled = True
                    if estado == 'descubierta':
                        num = tablero.numeros[f][c]
                        label = '.' if num == 0 else str(num)
                    elif estado == 'bandera':
                        label = '🚩'
                    elif tablero.game_over and tablero.minas[f][c]:
                        label = '💣'
                    else:
                        label = '🚩' if modo_bandera else '?'
                        disabled = False
                    with cols[c]:
                        if st.button(label, key=f"h_{f}_{c}", disabled=disabled,
                                     use_container_width=True):
                            if not tablero.game_over and not tablero.won:
                                if modo_bandera and estado == 'oculta':
                                    tablero.marcar_bandera(f, c)
                                    st.rerun()
                                elif not modo_bandera and estado == 'oculta':
                                    tablero.descubrir(f, c)
                                    st.session_state.movidas_humano += 1
                                    if tablero.game_over or tablero.won:
                                        st.session_state.tiempo_humano = time.time() - st.session_state.inicio
                                        verificar_resultado()
                                    st.rerun()

        if st.session_state.modo == 'Demo Bot':
            bt = st.session_state.bot_tablero
            if bt.game_over:
                for f in range(filas):
                    for c in range(columnas):
                        if bt.minas[f][c] and bt.estado[f][c] != 'bandera':
                            bt.estado[f][c] = 'descubierta'
        else:
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
            elif 'Derrota' in r:
                st.error(f"### 💥 {r}")
            else:
                st.info(f"### 🤝 {r}")

            if not st.session_state.partida_guardada:
                if st.session_state.modo == 'Demo Bot':
                    bt = st.session_state.bot_tablero
                    g = build_constraint_graph(bt)
                    met = metricas_grafo(g)
                    agregar_partida(
                        modo=st.session_state.modo, dificultad=dificultad, resultado=r,
                        tiempo=st.session_state.tiempo_bot,
                        filas=filas, columnas=columnas, minas=minas,
                        movidas_humano=0, movidas_bot=st.session_state.movidas_bot,
                        nodos_grafo=met['nodos'], componentes=met['componentes']
                    )
                else:
                    g = build_constraint_graph(tablero)
                    met = metricas_grafo(g)
                    agregar_partida(
                        modo=st.session_state.modo, dificultad=dificultad, resultado=r,
                        tiempo=st.session_state.tiempo_humano,
                        filas=filas, columnas=columnas, minas=minas,
                        movidas_humano=st.session_state.movidas_humano,
                        movidas_bot=st.session_state.movidas_bot if es_vs_bot else 0,
                        nodos_grafo=met['nodos'], componentes=met['componentes']
                    )
                st.session_state.partida_guardada = True

            if st.button("🔄 Nueva partida", use_container_width=True):
                reiniciar()
                iniciar_partida()
                st.rerun()

    with tab_grafo:
        grafo_tablero = build_constraint_graph(tablero) if tablero else None
        st.subheader("📈 Grafo de restricciones")
        if grafo_tablero and grafo_tablero.number_of_nodes() > 0:
            subproblemas = particionar_tablero(tablero)
            fig = dibujar_grafo(grafo_tablero, [sp['nodos'] for sp in subproblemas], mostrar=False)
            st.pyplot(fig)
        else:
            st.info("Aún no hay casillas frontera. Descubre más casillas en el tablero.")
        bt = st.session_state.bot_tablero
        if bt and bt is not tablero:
            st.subheader("🤖 Grafo del Bot")
            g_bot = build_constraint_graph(bt)
            comps_bot = obtener_componentes(g_bot)
            if g_bot.number_of_nodes() > 0:
                fig2 = dibujar_grafo(g_bot, comps_bot, mostrar=False, titulo='Grafo del Bot')
                st.pyplot(fig2)

    with tab_detalle:
        st.subheader("📊 Métricas del grafo")
        if grafo_tablero and grafo_tablero.number_of_nodes() > 0:
            met = metricas_grafo(grafo_tablero)
            subproblemas = particionar_tablero(tablero)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Nodos", met['nodos'])
            c2.metric("Aristas", met['aristas'])
            c3.metric("Componentes", met['componentes'])
            c4.metric("Comp. más grande", met['componente_mas_grande'])
            c1.metric("Densidad", f"{met['densidad']:.3f}")
            c2.metric("Grado promedio", f"{met['grado_promedio']:.2f}")
            c3.metric("Coef. agrupamiento", f"{met['coeficiente_agrupamiento']:.3f}")
            with st.expander("🔍 Detalle de componentes"):
                for i, sp in enumerate(subproblemas):
                    st.markdown(f"**Componente {i+1}:** {len(sp['nodos'])} casillas, {len(sp['restricciones'])} restricciones")
                    st.write(f"Nodos: {sorted(sp['nodos'])}")
                    for pos, restr in sp['restricciones'].items():
                        st.write(f"  ({pos[0]},{pos[1]}) → {restr['valor']}, vecinas: {sorted(restr['vecinas_ocultas'])}")
        else:
            st.info("No hay datos de grafo disponibles aún.")


def pagina_inicio():
    st.title("💣 Buscaminas Inteligente")
    st.markdown(f"""
    <div class="card" style="text-align:center;border:2px solid {C_NEON['accent']};">
        <span style="font-size:3rem;">🧠</span>
        <h3 style="color:{C_NEON['accent']};">Entrena tu juego con teoría de grafos</h3>
        <p style="color:{C_NEON['muted']};">Modela el tablero como grafo de restricciones, divídelo en componentes independientes y compite contra una IA basada en CSP.</p>
    </div>
    """, unsafe_allow_html=True)

    hist = cargar_historial()
    if hist:
        st.subheader("📊 Resumen global")
        total = len(hist)
        wins = sum(1 for p in hist if 'Victoria' in p['resultado'])
        rango, wr = calcular_rango(hist)
        ca1, ca2, ca3, ca4 = st.columns(4)
        ca1.markdown(f"<div class='card'><div class='stat-label'>Partidas</div><div class='stat-number'>{total}</div></div>", unsafe_allow_html=True)
        ca2.markdown(f"<div class='card'><div class='stat-label'>Victorias</div><div class='stat-number' style='color:{C_NEON['success']};'>{wins}</div></div>", unsafe_allow_html=True)
        ca3.markdown(f"<div class='card'><div class='stat-label'>Win Rate</div><div class='stat-number'>{wr:.1f}%</div></div>", unsafe_allow_html=True)
        ca4.markdown(f"<div class='card'><div class='stat-label'>Rango</div><div class='stat-number' style='color:{RANKOS[rango]['color']};'>{RANKOS[rango]['icon']} {rango}</div></div>", unsafe_allow_html=True)
    else:
        st.info("👈 Ve a **Jugar** en el menú lateral para comenzar tu primera partida")


def main():
    inicializar_estado()
    css_gamer()

    with st.sidebar:
        st.markdown("### 🧭 Menú")
        c_act = st.session_state.pagina_activa
        nav_opts = {'🏠 Inicio': 'Inicio', '🎮 Jugar': 'Jugar',
                    '🏆 Perfil': 'Perfil', '⏱ Tiempos': 'Tiempos'}
        nombres = list(nav_opts.keys())
        valores = list(nav_opts.values())
        idx = valores.index(c_act) if c_act in valores else 0
        sel = st.radio("", nombres, index=idx)
        st.session_state.pagina_activa = nav_opts[sel]

        if st.session_state.pagina_activa == 'Jugar' and st.session_state.partida_iniciada:
            st.divider()
            st.markdown("### ⚙️ Juego")
            dif = st.selectbox("Dificultad", list(DIFICULTADES.keys()),
                               key='dificultad_sel',
                               index=list(DIFICULTADES.keys()).index(st.session_state.dificultad))
            if dif != st.session_state.dificultad:
                st.session_state.dificultad = dif
                reiniciar()
                iniciar_partida()
                st.rerun()
            if dif == 'Personalizado':
                st.number_input("Filas", 3, 20, 9, key='cfg_filas')
                st.number_input("Columnas", 3, 20, 9, key='cfg_columnas')
                max_minas = st.session_state.get('cfg_filas', 9) * st.session_state.get('cfg_columnas', 9) - 1
                st.number_input("Minas", 1, max_minas, 10, key='cfg_minas')
            if st.button("🔄 Reiniciar partida", type="primary", use_container_width=True):
                reiniciar()
                iniciar_partida()
                st.rerun()

        hist = cargar_historial()
        if hist:
            st.divider()
            rango, wr = calcular_rango(hist)
            total = len(hist)
            info = RANKOS[rango]
            st.markdown(f"""
            <div style="text-align:center;padding:10px;background:{C_NEON['card']};border-radius:10px;border:1px solid {info['color']};">
                <span style="font-size:1.5rem;">{info['icon']}</span><br>
                <span style="color:{info['color']};font-weight:bold;">{rango}</span><br>
                <span style="color:{C_NEON['muted']};font-size:0.7rem;">{total} partidas · {wr:.1f}% WR</span>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                "📥 Exportar historial",
                data=json.dumps(hist, indent=2),
                file_name='historial_partidas.json',
                mime='application/json',
                use_container_width=True
            )

    if st.session_state.pagina_activa == 'Inicio':
        pagina_inicio()
    elif st.session_state.pagina_activa == 'Jugar':
        pagina_juego()
    elif st.session_state.pagina_activa == 'Perfil':
        pagina_perfil()
    elif st.session_state.pagina_activa == 'Tiempos':
        pagina_tiempos()


if __name__ == '__main__':
    main()
