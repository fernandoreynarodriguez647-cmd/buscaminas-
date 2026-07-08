import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.board import Board
from src.graph_builder import obtener_restricciones, build_constraint_graph


def test_obtener_restricciones():
    board = Board(5, 5, 3)
    board.descubrir(2, 2)
    restricciones = obtener_restricciones(board)
    assert isinstance(restricciones, dict)


def test_build_constraint_graph_3x3_center():
    board = Board(3, 3, 0)
    board.minas[0][0] = True
    board._calcular_numeros()
    board.descubrir(1, 1)
    grafo = build_constraint_graph(board)
    assert grafo.number_of_nodes() == 8
    aristas_completas = 8 * 7 // 2
    assert grafo.number_of_edges() == aristas_completas


def test_build_constraint_graph_no_frontera():
    board = Board(3, 3, 0)
    board.descubrir(0, 0)
    grafo = build_constraint_graph(board)
    assert grafo.number_of_nodes() == 0
    assert grafo.number_of_edges() == 0


def test_obtener_restricciones_con_minas():
    board = Board(5, 5, 0)
    board.minas[0][1] = True
    board.minas[1][0] = True
    board.minas[1][1] = True
    board._calcular_numeros()
    board.descubrir(2, 2)
    restricciones = obtener_restricciones(board)
    if restricciones:
        for pos, restr in restricciones.items():
            assert restr['valor'] > 0
            for coord in restr['vecinas_ocultas']:
                assert board.estado[coord[0]][coord[1]] == 'oculta'


if __name__ == '__main__':
    test_obtener_restricciones()
    test_build_constraint_graph_3x3_center()
    test_build_constraint_graph_no_frontera()
    test_obtener_restricciones_con_minas()
    print("Todos los tests de graph_builder pasaron.")
