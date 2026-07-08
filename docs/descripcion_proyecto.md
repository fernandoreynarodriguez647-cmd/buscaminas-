# Descripción del Proyecto — Buscaminas Inteligente (Módulo de Grafos)

## Objetivo

Construir un sistema completo de entrenamiento para Buscaminas basado en teoría de grafos y CSP. El sistema modela el tablero como un grafo de restricciones, lo divide en componentes independientes y permite tanto el juego manual como la competencia contra una IA.

## Justificación

Resolver todo el tablero de Buscaminas de una sola vez es computacionalmente costoso (exponencial en el número de casillas ocultas). Al particionar el problema en componentes independientes mediante teoría de grafos, cada subproblema se resuelve rápido por separado.

Además, el modo competitivo (humano vs bot) permite al jugador aprender estrategias óptimas observando las decisiones de la IA, que usa CSP con AC-3 para deducir lógicamente minas y casillas seguras.

## Flujo completo

```
Board → obtener_casillas_frontera()
  → graph_builder.build_constraint_graph()
    → graph_analysis.particionar_tablero()
      → lista de subproblemas independientes
        → solver_csp.MinesweeperCSP (CSP + AC-3)
          → deduce minas y casillas seguras por componente
```

## Arquitectura detallada

### `src/board.py` — Tablero

Clase `Board` con toda la lógica del juego:

- **Constructor**: coloca minas aleatoriamente, calcula números de cada casilla
- **descubrir(f, c)**: descubre con flood fill recursivo para casillas 0. Si la casilla tiene mina, `game_over = True`
- **marcar_bandera(f, c)**: alterna bandera; actualiza contadores de banderas y minas marcadas
- **obtener_casillas_frontera()**: casillas ocultas con al menos un vecino descubierto numerado
- **obtener_todas_ocultas()**: todas las casillas aún ocultas
- **clonar_para_bot()**: deep copy para que el bot juegue en un tablero independiente
- **minas_restantes()**: `num_minas - banderas_colocadas`
- **Atributos de estado**: `game_over`, `won`, `banderas_colocadas`, `descubiertas`

### `src/graph_builder.py` — Construcción del grafo

- **obtener_restricciones(board)**: recorre casillas descubiertas con número > 0 y construye:
  ```python
  {(f, c): {'valor': int, 'vecinas_ocultas': set()}}
  ```
- **build_constraint_graph(board)**: grafo no dirigido donde los nodos son casillas frontera y las aristas conectan casillas que comparten restricción (se forma un clique por cada restricción)

### `src/graph_analysis.py` — Análisis de grafos

- **obtener_componentes(grafo)**: `networkx.connected_components()`
- **metricas_grafo(grafo)**: devuelve nodos, aristas, componentes, densidad, grado promedio, componente más grande, coeficiente de agrupamiento
- **particionar_tablero(board)**: construye grafo, obtiene componentes, filtra restricciones relevantes y devuelve lista de `{'nodos': set, 'restricciones': dict}`

### `src/solver_csp.py` — Solver CSP y Bot

**MinesweeperCSP** — Aplica AC-3 (Arc Consistency) sobre cada componente:

1. Inicializa con el tablero actual
2. Obtiene restricciones y grafo
3. Por cada componente:
   - Aplica reglas de deducción:
     - Si `número == len(vecinas_ocultas)`: todas son minas → marcarlas
     - Si `número == 0`: todas son seguras → descubrirlas
     - Itera hasta que no haya más cambios (punto fijo)
   - Si no se pudo deducir nada, elige la casilla de menor riesgo probabilístico (basado en la relación valor/vecinas de las restricciones)

**BotJugador** — Estrategia de juego:

1. Ejecuta el CSP para obtener minas y casillas seguras
2. Prioriza: descubrir seguras → marcar minas → azar con menor riesgo
3. Juega turno a turno, compatible con Streamlit para visualización paso a paso

### `src/visualizer.py` — Visualización

- **dibujar_grafo()**: grafo con spring layout, nodos coloreados por componente, tamaño según grado, métricas en el título
- **dibujar_grafo_comparativa()**: dos gráficos lado a lado (humano vs bot) para comparación visual

## Dashboard interactivo (Streamlit)

`streamlit_app.py` — Interfaz web completa con tres modos:

### Modo Practicar
- Juego clásico de Buscaminas con configuración de dificultad
- Visualización en tiempo real del grafo de restricciones
- Métricas detalladas: nodos, aristas, componentes, densidad, grado promedio
- Exploración expandible de cada componente y sus restricciones

### Modo Vs Bot
- Humano y bot juegan en tableros idénticos (mismas minas)
- Timer independiente para cada jugador
- El humano hace clics; el bot avanza con un botón "Turno del Bot"
- Al finalizar, comparativa visual de los grafos de ambos jugadores
- Resultado: gana quien termina primero (o el que logra victoria si el otro pierde)

### Modo Demo Bot
- El bot juega automáticamente en tiempo real
- Ideal para observar estrategias óptimas de la IA

### Historial de partidas
- Persistente en archivo JSON (`historial_partidas.json`)
- Estadísticas globales: total, victorias, derrotas, win rate
- Exportación a JSON descargable
- Vista detallada de cada partida con todas las métricas

## Tests

### tests/test_graph_builder.py (4 tests)
- Verifica extracción de restricciones
- Grafo 3×3 completamente conectado con centro numerado
- Grafo vacío sin frontera
- Restricciones con minas manuales

### tests/test_graph_analysis.py (6 tests)
- Componentes: dos grupos, un grupo, vacío
- Particionar tablero 3×3
- Métricas: grafo vacío, grafo completo K5

### tests/test_solver_csp.py (3 tests)
- CSP resuelve 8 vecinas con mina en esquina
- Bot realiza un movimiento válido
- CSP sin restricciones devuelve vacío

## Tecnologías

| Tecnología | Versión | Propósito |
|---|---|---|
| Python | 3.10+ | Lenguaje principal |
| networkx | 3.4+ | Grafos y análisis |
| matplotlib | 3.10+ | Visualización |
| streamlit | 1.59+ | Dashboard web |
| numpy | 2.2+ | Cómputos numéricos |

## Dificultades predefinidas

| Dificultad | Filas | Columnas | Minas |
|---|---|---|---|
| Principiante | 9 | 9 | 10 |
| Intermedio | 16 | 16 | 40 |
| Experto | 16 | 30 | 99 |
| Personalizado | configurable | configurable | configurable |

## Repositorio

```
https://github.com/fernandoreynarodriguez647-cmd/buscaminas-.git
```

## Estado del proyecto

- ✅ Módulo Board (con estado de juego completo)
- ✅ Módulo de Grafos (restricciones, construcción, partición)
- ✅ Métricas de grafos (densidad, grado, agrupamiento)
- ✅ Solver CSP con AC-3
- ✅ Bot jugador inteligente
- ✅ Visualización matplotlib (individual y comparativa)
- ✅ Dashboard Streamlit (3 modos de juego)
- ✅ Timer y estadísticas en vivo
- ✅ Historial de partidas persistente
- ✅ Tests unitarios (13 tests)
- ✅ Repositorio en GitHub
