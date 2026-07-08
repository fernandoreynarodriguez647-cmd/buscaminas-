import networkx as nx
from src.graph_builder import obtener_restricciones, build_constraint_graph


def obtener_componentes(grafo):
    return list(nx.connected_components(grafo))


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
