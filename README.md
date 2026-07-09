# Buscaminas Inteligente — Módulo de Grafos

Proyecto académico que aplica teoría de grafos, CSP (Constraint Satisfaction Problems) y AC-3 al juego Buscaminas. Incluye un dashboard interactivo con Streamlit para jugar, entrenar y competir contra una IA.

## Flujo del sistema

```
Board → obtener_casillas_frontera() → build_constraint_graph()
→ particionar_tablero() → lista de subproblemas → solver_csp.py (CSP + AC-3)
```

## Requisitos

```bash
pip install -r requirements.txt
```

## Estructura

```
buscaminas_grafos/
├── src/
│   ├── board.py            # Lógica del tablero
│   ├── graph_builder.py    # Grafo de restricciones
│   ├── graph_analysis.py   # Componentes conexas + métricas
│   ├── solver_csp.py       # CSP + Bot jugador inteligente
│   └── visualizer.py       # Visualización matplotlib
├── tests/
│   ├── test_graph_builder.py
│   ├── test_graph_analysis.py
│   └── test_solver_csp.py
├── streamlit_app.py        # Dashboard web
└── requirements.txt
```

## Uso

### Dashboard web (recomendado)

```bash
streamlit run streamlit_app.py
```

Navegación: menú lateral con Inicio, Jugar, Perfil, Tiempos.

### Modos de juego

| Modo | Descripción |
|------|-------------|
| **Practicar** | Juega solo, observa el grafo de restricciones en tiempo real |
| **Vs Bot** | Humano y bot comparten el mismo tablero. Gana quien lo resuelva primero |
| **Demo Bot** | Observa al bot resolver paso a paso con explicaciones detalladas |

### Funcionalidades

- Dificultades: Principiante (9×9, 10 minas), Intermedio (16×16, 40), Experto (16×30, 99), Personalizado
- Timer en tiempo real para humano y bot
- Botón "← Volver" en cada página para navegación rápida
- Botón "← Inicio" en Perfil y Tiempos
- En Vs Bot: el bot avanza 3 pasos por click con explicación CSP
- En Demo Bot: bot paso a paso con resaltado visual de la última jugada
- Visualización del grafo coloreado por componentes conexas
- Métricas: nodos, aristas, componentes, densidad, grado promedio, agrupamiento
- Historial de partidas persistente con estadísticas globales
- Sistema de rangos: Bronce → Plata → Oro según win rate y partidas
- Podio de mejores tiempos por dificultad
- Exportación de historial a JSON

### Tests

```bash
python tests/test_graph_builder.py
python tests/test_graph_analysis.py
python tests/test_solver_csp.py
```

## Módulos

### `board.py` — Clase Board

- Administra el tablero, minas, números, descubrimiento con flood fill
- `game_over`, `won`, `banderas_colocadas`, `minas_restantes()` para estado de juego
- `obtener_casillas_frontera()`: casillas ocultas relevantes para el grafo
- `obtener_todas_ocultas()`: todas las casillas aún ocultas

### `graph_builder.py` — Grafo de restricciones

- `obtener_restricciones(board)`: extrae las restricciones de celdas descubiertas con número > 0
- `build_constraint_graph(board)`: construye `networkx.Graph` con cliques por restricción

### `graph_analysis.py` — Componentes y métricas

- `obtener_componentes(grafo)`: componentes conexas con `networkx.connected_components`
- `metricas_grafo(grafo)`: nodos, aristas, componentes, densidad, grado promedio, componente más grande, coeficiente de agrupamiento
- `particionar_tablero(board)`: construye grafo, particiona y devuelve subproblemas con nodos + restricciones

### `solver_csp.py` — Solver CSP y Bot

- `MinesweeperCSP`: aplica AC-3 para deducir minas y casillas seguras de cada componente
- `BotJugador`: usa el CSP para jugar automáticamente; prioriza deducciones seguras, luego elige la casilla de menor riesgo probabilístico

### `visualizer.py` — Visualización

- `dibujar_grafo()`: grafo coloreado, tamaño de nodos según grado, métricas en título

## Repositorio

GitHub: https://github.com/fernandoreynarodriguez647-cmd/buscaminas-.git
