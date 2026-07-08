import networkx as nx
from src.graph_builder import obtener_restricciones, build_constraint_graph


def obtener_componentes(grafo):
    return list(nx.connected_components(grafo))


def metricas_grafo(grafo):
    if grafo.number_of_nodes() == 0:
        return {
            'nodos': 0,
            'aristas': 0,
            'componentes': 0,
            'densidad': 0.0,
            'grado_promedio': 0.0,
            'componente_mas_grande': 0,
            'coeficiente_agrupamiento': 0.0
        }
    componentes = obtener_componentes(grafo)
    comp_grande = max(len(c) for c in componentes) if componentes else 0
    try:
        coef = nx.average_clustering(grafo)
    except ZeroDivisionError:
        coef = 0.0
    return {
        'nodos': grafo.number_of_nodes(),
        'aristas': grafo.number_of_edges(),
        'componentes': len(componentes),
        'densidad': nx.density(grafo),
        'grado_promedio': sum(d for _, d in grafo.degree()) / grafo.number_of_nodes() if grafo.number_of_nodes() > 0 else 0,
        'componente_mas_grande': comp_grande,
        'coeficiente_agrupamiento': coef
    }


def particionar_tablero(board):
    grafo = build_constraint_graph(board)
    restricciones = obtener_restricciones(board)
    componentes = obtener_componentes(grafo)
    subproblemas = []
    for comp in componentes:
        restricciones_comp = {}
        for pos, restr in restricciones.items():
            if restr['vecinas_ocultas'] & comp:
                restricciones_comp[pos] = restr
        subproblemas.append({
            'nodos': comp,
            'restricciones': restricciones_comp
        })
    return subproblemas
