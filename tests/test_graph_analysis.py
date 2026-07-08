import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.graph_analysis import obtener_componentes, particionar_tablero, metricas_grafo
from src.board import Board
import networkx as nx


def test_obtener_componentes_dos_grupos():
    grafo = nx.Graph()
    grafo.add_edges_from([(0, 1), (1, 2)])
    grafo.add_edges_from([(3, 4)])
    componentes = obtener_componentes(grafo)
    assert len(componentes) == 2


def test_obtener_componentes_un_grupo():
    grafo = nx.Graph()
    grafo.add_edges_from([(0, 1), (1, 2), (2, 0)])
    componentes = obtener_componentes(grafo)
    assert len(componentes) == 1


def test_obtener_componentes_vacio():
    grafo = nx.Graph()
    componentes = obtener_componentes(grafo)
    assert len(componentes) == 0


def test_particionar_tablero_3x3():
    board = Board(3, 3, 0)
    board.minas[0][0] = True
    board._calcular_numeros()
    board.descubrir(1, 1)
    subproblemas = particionar_tablero(board)
    assert len(subproblemas) >= 1
    for sp in subproblemas:
        assert 'nodos' in sp
        assert 'restricciones' in sp


def test_metricas_grafo_vacio():
    grafo = nx.Graph()
    met = metricas_grafo(grafo)
    assert met['nodos'] == 0
    assert met['aristas'] == 0
    assert met['componentes'] == 0


def test_metricas_grafo_con_nodos():
    grafo = nx.complete_graph(5)
    met = metricas_grafo(grafo)
    assert met['nodos'] == 5
    assert met['aristas'] == 10
    assert met['componentes'] == 1
    assert met['densidad'] == 1.0


if __name__ == '__main__':
    test_obtener_componentes_dos_grupos()
    test_obtener_componentes_un_grupo()
    test_obtener_componentes_vacio()
    test_particionar_tablero_3x3()
    test_metricas_grafo_vacio()
    test_metricas_grafo_con_nodos()
    print("Todos los tests de graph_analysis pasaron.")
