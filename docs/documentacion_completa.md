# Documentación Completa del Proyecto: Buscaminas Inteligente — Módulo de Grafos

---

## 1. Descripción General

**Buscaminas Inteligente** es un proyecto académico que aplica **teoría de grafos**, **CSP (Constraint Satisfaction Problems)** y el algoritmo **AC-3 (Arc Consistency 3)** al clásico juego Buscaminas. Incluye un dashboard interactivo web construido con **Streamlit** para jugar, entrenar y competir contra una IA.

---

## 2. Propósito y Objetivo

El objetivo principal es construir un sistema completo de entrenamiento para Buscaminas que:

- Modele el tablero como un **grafo de restricciones**
- Divida el problema en **componentes independientes** para hacerlo computacionalmente tratable
- Use **CSP con AC-3** para deducir lógicamente minas y casillas seguras
- Permita **juego manual**, **competencia humano vs IA**, y **demostración paso a paso** de la IA
- Proporcione **métricas de grafo** para entender la estructura del problema

---

## 3. ¿A quién está dirigido?

- **Estudiantes** de algoritmos, teoría de grafos e inteligencia artificial
- **Jugadores** de Buscaminas que quieren mejorar aprendiendo de una IA
- **Entusiastas** de la IA y sistemas basados en reglas lógicas

---

## 4. Justificación Técnica

Resolver todo el tablero de Buscaminas de una sola vez es **exponencial** en el número de casillas ocultas. Al **particionar el problema en componentes independientes** mediante teoría de grafos, cada subproblema se resuelve por separado de forma mucho más eficiente.

El sistema usa **CSP + AC-3** porque:
- El Buscaminas es naturalmente un problema de restricciones: cada número en una casilla descubierta es una restricción sobre las minas en sus vecinas
- AC-3 propaga estas restricciones hasta alcanzar un punto fijo
- Las componentes conexas del grafo de restricciones son subproblemas independientes que se pueden resolver por separado

---

## 5. Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|---|---|---|
| **Python** | 3.10+ | Lenguaje principal de programación |
| **NetworkX** | 3.4+ | Creación, manipulación y análisis de grafos |
| **Matplotlib** | 3.10+ | Visualización de grafos en 2D |
| **Streamlit** | 1.59+ | Framework para dashboard web interactivo |
| **NumPy** | 2.2+ | Cómputos numéricos auxiliares |
| **JSON** | estándar | Persistencia del historial de partidas |

---

## 6. Estructura del Proyecto

```
buscaminas_grafos/
├── src/                          # Código fuente principal
│   ├── __init__.py              # Marca src/ como paquete Python
│   ├── board.py                 # Lógica del tablero de Buscaminas
│   ├── graph_builder.py         # Construcción del grafo de restricciones
│   ├── graph_analysis.py        # Componentes conexas y métricas de grafo
│   ├── solver_csp.py            # Solver CSP y Bot jugador inteligente
│   └── visualizer.py            # Visualización de grafos con matplotlib
├── tests/                        # Tests unitarios
│   ├── __init__.py
│   ├── test_graph_builder.py    # 4 tests: restricciones y construcción de grafo
│   ├── test_graph_analysis.py   # 6 tests: componentes, partición, métricas
│   └── test_solver_csp.py       # 3 tests: CSP y Bot
├── docs/                         # Documentación
│   ├── descripcion_proyecto.md  # Descripción previa del proyecto
│   └── documentacion_completa.md # Este documento
├── streamlit_app.py             # Dashboard web Streamlit (892 líneas)
├── main.py                      # Punto de entrada para ejecución en consola
├── requirements.txt             # Dependencias del proyecto
├── historial_partidas.json      # Archivo de persistencia (partidas guardadas)
├── .gitignore                   # Archivos ignorados por git
├── README.md                    # Documentación de inicio rápido
├── notebooks/                   # Carpeta para Jupyter notebooks (vacía)
└── venv/                        # Entorno virtual de Python
```

---

## 7. Funcionamiento Detallado de Cada Módulo

### 7.1 `src/board.py` — Clase Board (Tablero)

**Propósito**: Administrar toda la lógica del juego Buscaminas: estado del tablero, minas, números, descubrimiento de casillas, marcado de banderas y detección de victoria/derrota.

**Atributos principales**:
- `filas`, `columnas` — Dimensiones del tablero
- `num_minas` — Cantidad total de minas
- `estado[][]` — Matriz de estados: `'oculta'`, `'descubierta'`, `'bandera'`
- `minas[][]` — Matriz booleana: `True` si hay mina
- `numeros[][]` — Matriz con la cuenta de minas vecinas por casilla
- `game_over` — Booleano: `True` si se pisó una mina
- `won` — Booleano: `True` si se descubrieron todas las casillas seguras
- `banderas_colocadas` — Contador de banderas puestas
- `descubiertas` — Contador de casillas descubiertas
- `minas_marcadas` — Contador de minas correctamente marcadas con bandera

**Métodos principales**:

| Método | Función |
|---|---|
| `__init__(filas, columnas, num_minas, minas_predefinidas=None)` | Constructor: crea tablero vacío, coloca minas (aleatorias o predefinidas), calcula números |
| `_colocar_minas()` | Coloca `num_minas` minas en posiciones aleatorias del tablero usando `random.randint` y un bucle con conjunto para evitar duplicados |
| `_calcular_numeros()` | Por cada casilla sin mina, cuenta cuántas de sus 8 vecinas tienen mina y almacena ese número |
| `_vecinos(f, c)` | Devuelve lista de coordenadas de las 8 casillas adyacentes (horizontal, vertical, diagonal) que están dentro del tablero |
| `descubrir(f, c)` | Descubre una casilla: si es mina → `game_over`; si no, la marca como descubierta; si el número es 0, aplica **flood fill recursivo** para descubrir automáticamente todas las casillas vacías adyacentes |
| `marcar_bandera(f, c)` | Alterna entre oculta ↔ bandera; actualiza contadores de banderas y minas marcadas |
| `_verificar_victoria()` | Si `descubiertas >= total_seguras` (total de casillas sin mina), establece `won = True` |
| `minas_restantes()` | Retorna `num_minas - banderas_colocadas` |
| `obtener_casillas_frontera()` | Retorna conjunto de casillas ocultas que tienen al menos un vecino descubierto con número > 0. **Fundamental para el grafo de restricciones** |
| `obtener_todas_ocultas()` | Retorna conjunto de todas las casillas aún ocultas (sin descubrir ni marcadas) |
| `clonar_para_bot()` | Crea una copia profunda (`copy.deepcopy`) del tablero para que el bot juegue en su propia copia |
| `__str__()` | Representación textual: `?` oculta, `F` bandera, `X` mina, `.` vacía, `1-8` números |

**Algoritmo de flood fill**: Cuando se descubre una casilla con número 0, recursivamente descubre todas sus vecinas ocultas. Si alguna de esas vecinas también es 0, continúa la recursión. Esto replica el comportamiento clásico del Buscaminas donde las zonas vacías se expanden automáticamente.

---

### 7.2 `src/graph_builder.py` — Grafo de Restricciones

**Propósito**: Construir el **grafo de restricciones** del Buscaminas, donde los nodos son casillas frontera (ocultas pero con vecinos descubiertos) y las aristas conectan casillas que comparten una restricción.

**Funciones**:

#### `obtener_restricciones(board)`
- Recorre todas las casillas del tablero
- Para cada casilla **descubierta con número > 0**, encuentra sus vecinas ocultas
- Retorna un diccionario:
  ```python
  {
    (f, c): {
      'valor': <número de la casilla>,
      'vecinas_ocultas': {(f1,c1), (f2,c2), ...}
    }
  }
  ```
- Cada entrada es una **restricción**: "entre estas vecinas ocultas hay exactamente `valor` minas"

#### `build_constraint_graph(board)`
- Llama a `obtener_restricciones()` para obtener todas las restricciones
- Crea un `networkx.Graph` (no dirigido)
- Por cada restricción, añade todos sus nodos (vecinas ocultas) al grafo
- Conecta todos los nodos de cada restricción formando un **clique** (grafo completo entre esos nodos)
- **Fundamento**: si dos casillas comparten una restricción, están relacionadas y deben estar conectadas en el grafo

**Ejemplo**: Si la casilla (2,2) tiene número 3 y sus vecinas ocultas son {(1,1), (1,2), (2,1)}, el grafo tendrá esos 3 nodos y 3 aristas conectándolos entre sí (triángulo).

---

### 7.3 `src/graph_analysis.py` — Análisis de Grafos

**Propósito**: Analizar el grafo de restricciones para obtener componentes conexas, métricas y particionar el tablero en subproblemas independientes.

**Funciones**:

#### `obtener_componentes(grafo)`
- Usa `networkx.connected_components()` para encontrar **componentes conexas**
- Retorna lista de conjuntos, donde cada conjunto contiene las coordenadas de una componente
- **Importancia**: cada componente es un subproblema **totalmente independiente** del resto

#### `metricas_grafo(grafo)`
- Calcula y retorna un diccionario con métricas del grafo:
  | Métrica | Significado |
  |---|---|
  | `nodos` | Número de casillas frontera en el grafo |
  | `aristas` | Número de conexiones entre casillas frontera |
  | `componentes` | Cantidad de subproblemas independientes |
  | `densidad` | Proporción de aristas existentes vs. posibles (`networkx.density`) |
  | `grado_promedio` | Promedio de conexiones por nodo |
  | `componente_mas_grande` | Tamaño (en nodos) de la componente más grande |
  | `coeficiente_agrupamiento` | Mide cuán agrupados están los nodos (`networkx.average_clustering`) |

#### `particionar_tablero(board)`
- Construye el grafo de restricciones completo
- Obtiene las componentes conexas
- Para cada componente, filtra SOLO las restricciones que involucran nodos de esa componente
- Retorna lista de subproblemas:
  ```python
  [
    {
      'nodos': {(f1,c1), (f2,c2), ...},
      'restricciones': {(f,c): {'valor': ..., 'vecinas_ocultas': set()}, ...}
    },
    ...
  ]
  ```
- **Clave del sistema**: cada subproblema se resuelve independientemente, reduciendo la complejidad exponencial a problemas pequeños manejables

---

### 7.4 `src/solver_csp.py` — Solver CSP y Bot

**Propósito**: Implementar un **solvers de Problemas de Satisfacción de Restricciones (CSP)** específico para Buscaminas y un Bot jugador que lo usa para jugar automáticamente.

#### Clase `MinesweeperCSP`

**Métodos**:

##### `__init__(board)`
- Almacena referencia al tablero
- Inicializa conjuntos vacíos de `known_mines` y `known_safe`

##### `resolver()`
1. Obtiene restricciones del tablero actual
2. Construye el grafo de restricciones
3. Obtiene componentes conexas
4. Por cada componente: llama a `_resolver_componente()`
5. Acumula minas y casillas seguras deducidas
6. Retorna `(minas_deducidas, seguras_deducidas)`

##### `_resolver_componente(restricciones, nodos)`
Aplica el **algoritmo AC-3 (Arc Consistency)** simplificado mediante iteración a punto fijo:

1. Convierte restricciones a lista de diccionarios
2. **Bucle de punto fijo**: repite hasta que no haya más cambios:
   - Por cada restricción:
     - **Regla 1**: Si `valor - minas_marcadas == 0` → todas las vecinas ocultas restantes son **seguras**
     - **Regla 2**: Si `len(vecinas) == valor - minas_marcadas` → todas son **minas**
3. Si no se dedujo nada (sin minas ni seguras), llama a `_elegir_menos_riesgoso()`
4. Retorna `(minas, seguras)`

##### `_elegir_menos_riesgoso(nodos, restricciones)`
- Calcula riesgo probabilístico para cada nodo como `valor / len(vecinas)` por restricción
- Toma el máximo riesgo entre todas las restricciones que afectan a cada nodo
- Elige aleatoriamente entre los nodos de menor riesgo
- **Fundamento**: si no hay certeza lógica, se elige la opción estadísticamente más segura

#### Clase `BotJugador`

**Propósito**: Estrategia de juego automática.

##### `__init__(board)`
- Guarda el tablero y crea una instancia de `MinesweeperCSP`

##### `jugar_turno()`
Estrategia en orden de prioridad:

| Prioridad | Acción | Condición |
|---|---|---|
| 1 | **Descubrir segura** | CSP dedujo casilla obligatoriamente segura |
| 2 | **Marcar mina** | CSP dedujo casilla obligatoriamente mina |
| 3 | **Adivinar frontera** | Elegir aleatoriamente entre casillas frontera sin mina |
| 4 | **Explorar ocultas** | Elegir aleatoriamente entre todas las ocultas sin mina |
| 5 | **No hacer nada** | Sin movimientos posibles |

Cada movimiento retorna una tupla `(acción, posición, explicación)` donde la explicación es una cadena descriptiva de por qué se tomó esa decisión. Esto es clave para el **modo Demo Bot**.

---

### 7.5 `src/visualizer.py` — Visualización de Grafos

**Propósito**: Generar visualizaciones gráficas del grafo de restricciones usando **matplotlib**.

#### `dibujar_grafo(grafo, componentes=None, mostrar=True, titulo=...)`
- Si el grafo está vacío, muestra un mensaje "Grafo vacío"
- Usa `networkx.spring_layout` (algoritmo de Fruchterman-Reingold) para posicionar nodos
- Colorea cada componente conexa con un color distinto (de una paleta de 10 colores)
- Tamaño de nodos proporcional a su grado (a más conexiones, más grande)
- Dibuja aristas semi-transparentes
- Etiqueta cada nodo con su coordenada `(f,c)`
- Muestra métricas en el título (nodos, aristas, componentes, densidad)
- Incluye leyenda de componentes
- Retorna la figura de matplotlib

#### `dibujar_grafo_comparativa(grafo_humano, comp_h, grafo_bot, comp_b)`
- Crea una figura con dos subplots lado a lado
- Muestra el grafo del humano y del bot simultáneamente
- Útil en el modo **Vs Bot** para comparar el progreso

---

### 7.6 `main.py` — Punto de Entrada en Consola

**Propósito**: Demostración en línea de comandos del sistema completo.

**Flujo**:
1. Crea un tablero 9×9 con 10 minas
2. Descubre la casilla central (4,4)
3. Muestra el tablero en texto
4. Construye el grafo de restricciones y muestra métricas
5. Particiona el tablero en componentes y muestra detalles
6. Dibuja el grafo (ventana matplotlib emergente)
7. Ejecuta el Bot de demostración que juega automáticamente

---

### 7.7 `streamlit_app.py` — Dashboard Web

**Propósito**: Interfaz de usuario interactiva y completa con 4 páginas y 3 modos de juego.

#### Arquitectura de la UI

**Menú lateral** (siempre visible):
- 🏠 Inicio
- 🎮 Jugar
- 🏆 Perfil
- ⏱ Tiempos
- Selector de dificultad (cuando está en Jugar)
- Botón "Reiniciar partida"
- Widget de rango actual y exportación de historial

#### Página: Inicio
- Título y descripción del proyecto
- Resumen global de estadísticas (partidas, victorias, win rate, rango)
- Llamado a la acción para ir a Jugar

#### Página: Jugar — 3 modos

**Modo Practicar**:
- Tablero interactivo: clic para descubrir, toggle para banderas
- Timer en tiempo real
- Contadores de minas restantes y banderas
- Al terminar: muestra resultado, guarda partida en historial
- Pestañas: Partida, Grafo (visualización dinámica), Detalle (métricas)

**Modo Vs Bot**:
- Humano y bot tienen tableros separados con **la misma distribución de minas**
- Timer independiente para cada jugador
- Bot avanza automáticamente con velocidad configurable
- El humano juega manualmente
- Gana quien resuelve primero
- Resultados detallados: Victoria/Derrota/Empate + quién fue más rápido

**Modo Demo Bot**:
- El bot juega solo paso a paso
- Botón "▶️ Iniciar Bot" y "⏭ Siguiente paso"
- **Resaltado visual** de la última casilla jugada por el bot
- Panel de **explicación detallada** de cada movimiento
- Ideal para aprendizaje: muestra el razonamiento CSP

#### Página: Perfil
- Insignia de rango con icono (Bronce 🥉, Plata 🥈, Oro 🥇)
- Tarjetas de estadísticas: partidas, victorias, derrotas, win rate
- Mejores tiempos por dificultad (mejor, promedio, último)
- Progreso hacia el siguiente rango
- Historial completo de partidas en expander

#### Página: Tiempos
- **Podio** con medallas 🥇🥈🥉 para los 3 mejores tiempos globales
- Top 10 de mejores tiempos en tabla

#### Sistema de Rangos

| Rango | Win Rate mínimo | Partidas mínimas | Color |
|---|---|---|---|
| Bronce 🥉 | 0% | 1 | #CD7F32 |
| Plata 🥈 | 45% | 5 | #C0C0C0 |
| Oro 🥇 | 70% | 15 | #FFD700 |

#### Persistencia

- `historial_partidas.json` guarda todas las partidas con:
  - Fecha, modo, dificultad, resultado, tiempo
  - Dimensiones del tablero, número de minas
  - Movidas del humano y del bot
  - Nodos del grafo y componentes
- Descargable desde la barra lateral
- Se carga automáticamente al iniciar la app

#### Esquema de colores "Gamer"
- Fondo oscuro (#0E1117)
- Acento neón verde (#00FF88)
- Acento naranja (#FF6B35)
- Acento azul (#00D4FF)
- Tarjetas con fondo semi-oscuro (#1A1D2E)

---

## 8. Flujo Completo del Sistema

```
1. JUGADOR (o Bot) descubre casilla inicial
       │
2. tablero.obtener_casillas_frontera()
       │
3. graph_builder.obtener_restricciones(board)
       │   Por cada casilla descubierta con número > 0:
       │     extraer vecinas ocultas + valor
       │
4. graph_builder.build_constraint_graph(board)
       │   Nodos = casillas frontera
       │   Aristas = cliques por cada restricción
       │
5. graph_analysis.particionar_tablero(board)
       │   Obtener componentes conexas
       │   Filtrar restricciones por componente
       │
6. Para CADA componente:
       │
7. solver_csp.MinesweeperCSP._resolver_componente()
       │   Aplicar AC-3 (punto fijo):
       │     - Si valor == 0 → todas seguras
       │     - Si len(vecinas) == valor → todas minas
       │   Si no hay certeza → menor riesgo probabilístico
       │
8. BotJugador.jugar_turno()
       │   Priorizar: descubrir seguras > marcar minas > adivinar
       │
9. Repetir hasta game_over o won
```

---

## 9. Tests Unitarios

### `test_graph_builder.py` (4 tests)

| Test | Descripción |
|---|---|
| `test_obtener_restricciones()` | Verifica que `obtener_restricciones()` retorna un diccionario |
| `test_build_constraint_graph_3x3_center()` | Tablero 3×3 sin minas excepto (0,0); descubre centro; verifica grafo completo (8 nodos, 28 aristas) |
| `test_build_constraint_graph_no_frontera()` | Tablero 3×3 sin minas; descubre (0,0); toda la esquina se descubre por flood fill; verifica grafo vacío |
| `test_obtener_restricciones_con_minas()` | Coloca 3 minas manuales; descubre (2,2); verifica que restricciones apunten solo a casillas ocultas |

### `test_graph_analysis.py` (6 tests)

| Test | Descripción |
|---|---|
| `test_obtener_componentes_dos_grupos()` | Grafo con dos subgrafos no conectados; verifica 2 componentes |
| `test_obtener_componentes_un_grupo()` | Grafo triángulo; verifica 1 componente |
| `test_obtener_componentes_vacio()` | Grafo vacío; verifica 0 componentes |
| `test_particionar_tablero_3x3()` | Tablero 3×3 con mina en (0,0); verifica partición retorna subproblemas con claves correctas |
| `test_metricas_grafo_vacio()` | Verifica métricas con 0 en todo para grafo vacío |
| `test_metricas_grafo_con_nodos()` | Grafo completo K5; verifica 5 nodos, 10 aristas, 1 componente, densidad 1.0 |

### `test_solver_csp.py` (3 tests)

| Test | Descripción |
|---|---|
| `test_csp_resuelve_8_vecinas()` | Tablero 3×3, mina en (0,0); verifica que CSP retorna conjuntos de minas y seguras |
| `test_bot_hace_movimiento()` | Tablero 5×5, descubre centro; verifica que bot retorna tupla válida con explicación |
| `test_csp_sin_restricciones()` | Tablero 3×3, descubre (0,0) que se expande por flood fill; verifica que CSP retorna vacío |

---

## 10. Dificultades Predefinidas

| Dificultad | Filas | Columnas | Minas | Densidad de minas |
|---|---|---|---|---|
| Principiante | 9 | 9 | 10 | ~12.3% |
| Intermedio | 16 | 16 | 40 | ~15.6% |
| Experto | 16 | 30 | 99 | ~20.6% |
| Personalizado | Configurable (3-20) | Configurable (3-20) | Configurable | Variable |

---

## 11. Decisiones de Diseño

1. **Componentes independientes**: En lugar de resolver todo el tablero como un solo CSP enorme, se particiona en componentes conexas. Cada componente es independiente de las demás (no comparten restricciones), lo que reduce drásticamente la complejidad.

2. **AC-3 simplificado**: En lugar de implementar AC-3 completo con cola de arcos, se usa un bucle de punto fijo que itera hasta que no hay cambios. Esto es equivalente para el Buscaminas porque las restricciones son estáticas.

3. **Misma distribución de minas en Vs Bot**: Se crean dos tableros con las mismas posiciones de minas para que la competencia sea justa, pero cada jugador descubre casillas de forma independiente.

4. **Bot determinista + aleatoriedad**: El bot usa CSP puro para deducciones lógicas (determinista), pero cuando no hay certeza, elige aleatoriamente entre las opciones de menor riesgo. Esto evita que el bot siempre juegue igual.

5. **Persistencia en JSON**: Se usa JSON (no base de datos) por simplicidad y portabilidad. Cada partida se guarda como un objeto en una lista.

---

## 12. Cómo Usar el Proyecto

### Dashboard web (recomendado)
```bash
streamlit run streamlit_app.py
```
Navegación por menú lateral: **Inicio → Jugar → Perfil → Tiempos**

### Consola (demostración)
```bash
python main.py
```
Ejecuta demo del bot y muestra grafo.

### Tests
```bash
python tests/test_graph_builder.py
python tests/test_graph_analysis.py
python tests/test_solver_csp.py
```

---

## 13. Estado del Proyecto

- ✅ Tablero completo con flood fill, banderas, detección de victoria/derrota
- ✅ Grafo de restricciones con cliques por restricción
- ✅ Partición en componentes independientes
- ✅ Métricas de grafo (densidad, grado, agrupamiento, etc.)
- ✅ Solver CSP con AC-3
- ✅ Bot jugador inteligente con 4 niveles de prioridad
- ✅ Visualización matplotlib con colores por componente
- ✅ Dashboard Streamlit con 3 modos de juego
- ✅ Vs Bot con tableros idénticos y velocidad configurable
- ✅ Demo Bot paso a paso con explicaciones y resaltado visual
- ✅ Sistema de rangos Bronce/Plata/Oro
- ✅ Podio y top 10 de mejores tiempos
- ✅ Historial persistente en JSON con exportación
- ✅ 13 tests unitarios
- ✅ Navegación con botones Volver/Inicio
- ✅ Repositorio en GitHub
