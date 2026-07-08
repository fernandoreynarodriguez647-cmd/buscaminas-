# Descripción del Proyecto — Buscaminas Inteligente (Módulo de Grafos)

## Objetivo

Construir la parte de teoría de grafos de un sistema de entrenamiento para Buscaminas. El grafo no resuelve el juego solo, sino que sirve para:

1. Tomar el estado actual del tablero
2. Identificar qué casillas ocultas importan (las que están en el borde de lo ya descubierto)
3. Modelarlas como grafo donde una arista entre dos casillas significa que están ligadas por la misma restricción numérica
4. Dividir ese grafo en componentes conexas (grupos independientes entre sí)
5. Entregar cada componente por separado para que después el módulo de CSP + AC-3 + backtracking resuelva cada grupo chico en vez de todo el tablero junto

## Justificación

Resolver todo el tablero de una sola vez es computacionalmente costoso. Al particionar el problema en componentes independientes, cada subproblema se resuelve rápido por separado, reduciendo drásticamente la complejidad.

## Flujo completo

```
Board (tablero)
  → obtener_casillas_frontera()
    → casillas ocultas relevantes
      → graph_builder.build_constraint_graph()
        → grafo de restricciones (networkx.Graph)
          → graph_analysis.obtener_componentes()
            → lista de componentes conexas
              → graph_analysis.particionar_tablero()
                → lista de subproblemas listos para CSP
                  → (siguiente etapa) solver_csp.py resuelve cada subproblema
```

## Arquitectura

### `src/board.py` — Tablero de Buscaminas

Clase `Board` que implementa toda la lógica del juego:

- **Inicialización**: coloca minas aleatoriamente y calcula los números de cada casilla
- **descubrir(f, c)**: descubre una casilla; si el número es 0, aplica flood fill recursivo para descubrir toda la región vacía
- **marcar_bandera(f, c)**: alterna el estado de bandera de una casilla oculta
- **obtener_casillas_frontera()**: método clave que devuelve las casillas ocultas que tienen al menos un vecino descubierto con número > 0. Estas son las únicas casillas relevantes para el grafo de restricciones
- **Atributos**:
  - `numeros[f][c]`: número de minas vecinas (solo para casillas descubiertas)
  - `estado[f][c]`: puede ser `'oculta'`, `'descubierta'` o `'bandera'`
  - `minas[f][c]`: `True` si hay mina, `False` en caso contrario

### `src/graph_builder.py` — Construcción del grafo

Dos funciones principales:

- **obtener_restricciones(board)**: recorre todas las casillas descubiertas con número mayor a 0 y construye un diccionario con la estructura:
  ```python
  {(f, c): {'valor': int, 'vecinas_ocultas': {(f1,c1), (f2,c2), ...}}}
  ```
  Cada entrada representa una restricción numérica del Buscaminas.

- **build_constraint_graph(board)**: construye un `networkx.Graph` no dirigido donde:
  - **Nodos**: casillas ocultas de la frontera
  - **Aristas**: conectan dos casillas frontera SI ambas son vecinas de la misma casilla numerada descubierta (no es vecindad geométrica directa, sino que comparten una restricción)
  - Para cada restricción, todas sus casillas ocultas se conectan formando un clique

### `src/graph_analysis.py` — Análisis y partición

- **obtener_componentes(grafo)**: usa `networkx.connected_components()` para separar el grafo en subgrupos sin conexión entre sí
- **particionar_tablero(board)**: función principal que:
  1. Construye el grafo con `build_constraint_graph()`
  2. Obtiene las restricciones con `obtener_restricciones()`
  3. Divide en componentes conexas
  4. Para cada componente, filtra solo las restricciones relevantes
  5. Devuelve lista de diccionarios `{'nodos': set, 'restricciones': dict}`

### `src/visualizer.py` — Visualización

- **dibujar_grafo(grafo, componentes, mostrar)**: dibuja el grafo con matplotlib y networkx usando disposición spring_layout. Si se pasan componentes, pinta cada uno de un color distinto. Devuelve la figura de matplotlib para poder usarla tanto en `plt.show()` como en `st.pyplot()`.

### `src/solver_csp.py` — Placeholder

Archivo vacío preparado para la siguiente etapa del proyecto: implementar un solver CSP con AC-3 y backtracking que resuelva cada subproblema generado por `particionar_tablero()`.

## Dashboard interactivo (Streamlit)

`streamlit_app.py` proporciona una interfaz web que permite:

- Configurar tamaño del tablero y cantidad de minas
- Descubrir casillas haciendo clic en una grilla
- Ver en tiempo real la construcción del grafo de restricciones
- Visualizar las componentes conexas con colores distintos
- Consultar métricas (nodos, aristas, componentes)
- Explorar el detalle de cada componente y sus restricciones

Ejecutar con:

```bash
streamlit run streamlit_app.py
```

## Tests

### `tests/test_graph_builder.py`

- `test_obtener_restricciones()`: verifica que obtener_restricciones devuelve un diccionario
- `test_build_constraint_graph_3x3_center()`: en tablero 3×3 con mina manual en (0,0) y celda central descubierta con número > 0, el grafo debe tener 8 nodos completamente conectados (28 aristas)
- `test_build_constraint_graph_no_frontera()`: con 0 minas, al descubrir (0,0) todo se vacía, el grafo debe tener 0 nodos y 0 aristas
- `test_obtener_restricciones_con_minas()`: verifica que las restricciones extraídas tengan valor > 0 y que todas sus vecinas ocultas realmente estén ocultas

### `tests/test_graph_analysis.py`

- `test_obtener_componentes_dos_grupos()`: grafo con un triángulo y una arista separada, debe devolver 2 componentes
- `test_obtener_componentes_un_grupo()`: grafo con un triángulo completo, debe devolver 1 componente
- `test_obtener_componentes_vacio()`: grafo vacío, debe devolver lista vacía
- `test_particionar_tablero_3x3()`: integración que verifica que particionar_tablero devuelve subproblemas con las llaves 'nodos' y 'restricciones'

## Tecnologías

| Tecnología | Versión | Propósito |
|---|---|---|
| Python | 3.10+ | Lenguaje principal |
| networkx | 3.4.2 | Grafos y análisis de componentes |
| matplotlib | 3.10.9 | Visualización del grafo |
| streamlit | 1.59.0 | Dashboard web interactivo |
| numpy | 2.2.6 | Cómputos numéricos |

## Repositorio

El proyecto está alojado en GitHub:

```
https://github.com/fernandoreynarodriguez647-cmd/buscaminas-.git
```

## Estado del proyecto

- ✅ Módulo de Board completo
- ✅ Módulo de Grafos (restricciones, construcción, partición)
- ✅ Visualización con matplotlib
- ✅ Dashboard interactivo con Streamlit
- ✅ Tests unitarios
- ✅ Repositorio en GitHub
- ⬜ Solver CSP (AC-3 + backtracking) — pendiente
