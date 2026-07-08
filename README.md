# Buscaminas Inteligente — Módulo de Grafos

Proyecto académico que aplica teoría de grafos y problemas de satisfacción de restricciones (CSP) al juego Buscaminas. Modela la lógica del tablero como un grafo de restricciones para dividir el problema en subproblemas independientes y resolverlos eficientemente.

## Flujo del sistema

```
Board → obtener_casillas_frontera() → graph_builder.build_constraint_graph()
→ graph_analysis.particionar_tablero() → lista de subproblemas → (futuro) solver_csp.py
```

## Requisitos

- Python 3.10+
- Librerías: networkx, matplotlib, numpy, streamlit

Instalación:

```bash
pip install -r requirements.txt
```

## Estructura del proyecto

```
buscaminas_grafos/
├── src/
│   ├── board.py            # Lógica del tablero de Buscaminas
│   ├── graph_builder.py    # Construcción del grafo de restricciones
│   ├── graph_analysis.py   # Partición en componentes independientes
│   ├── visualizer.py       # Visualización del grafo con matplotlib
│   └── solver_csp.py       # Placeholder para futuro solver CSP
├── tests/
│   ├── test_graph_builder.py
│   └── test_graph_analysis.py
├── main.py                 # Ejemplo completo por línea de comandos
├── streamlit_app.py        # Dashboard interactivo con Streamlit
├── requirements.txt
└── .gitignore
```

## Uso

### Línea de comandos

```bash
python main.py
```

Crea un tablero 9×9 con 10 minas, descubre la casilla central, construye el grafo, lo particiona en componentes y muestra la visualización.

### Dashboard web (Streamlit)

```bash
streamlit run streamlit_app.py
```

Abre una interfaz en el navegador (http://localhost:8501) con:
- Configuración de filas, columnas y minas
- Grilla interactiva para descubrir casillas con clics
- Visualización en tiempo real del grafo de restricciones coloreado por componentes
- Métricas: nodos, aristas, cantidad de componentes
- Detalle expandible de cada componente y sus restricciones

### Tests

```bash
python tests/test_graph_builder.py
python tests/test_graph_analysis.py
```

## Módulos

### `board.py` — Clase `Board`

- `Board(filas, columnas, num_minas)` — crea el tablero con minas aleatorias
- `descubrir(f, c)` — descubre una casilla con flood fill si es 0
- `marcar_bandera(f, c)` — pone o quita bandera
- `obtener_casillas_frontera()` — devuelve casillas ocultas con al menos un vecino numerado descubierto
- `_vecinos(f, c)` — lista de coordenadas vecinas válidas

### `graph_builder.py` — Construcción del grafo

- `obtener_restricciones(board)` — extrae restricciones de celdas numeradas descubiertas
- `build_constraint_graph(board)` — construye un `networkx.Graph` donde los nodos son casillas frontera y las aristas conectan casillas que comparten restricción

### `graph_analysis.py` — Análisis y partición

- `obtener_componentes(grafo)` — separa el grafo en componentes conexas
- `particionar_tablero(board)` — función principal: construye el grafo, lo divide en componentes y devuelve lista de subproblemas `{'nodos', 'restricciones'}`

### `visualizer.py` — Visualización

- `dibujar_grafo(grafo, componentes, mostrar)` — dibuja el grafo coloreado por componentes; devuelve la figura de matplotlib

## Repositorio

GitHub: https://github.com/fernandoreynarodriguez647-cmd/buscaminas-.git
