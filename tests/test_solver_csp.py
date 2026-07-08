import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.board import Board
from src.solver_csp import MinesweeperCSP, BotJugador


def test_csp_resuelve_8_vecinas():
    board = Board(3, 3, 0)
    board.minas[0][0] = True
    board._calcular_numeros()
    board.descubrir(1, 1)
    csp = MinesweeperCSP(board)
    minas, seguras = csp.resolver()
    assert isinstance(minas, set)
    assert isinstance(seguras, set)


def test_bot_hace_movimiento():
    board = Board(5, 5, 3)
    board.descubrir(2, 2)
    bot = BotJugador(board)
    accion, pos = bot.jugar_turno()
    assert accion in ('descubrir', 'marcar', 'nada')


def test_csp_sin_restricciones():
    board = Board(3, 3, 0)
    board.descubrir(0, 0)
    csp = MinesweeperCSP(board)
    minas, seguras = csp.resolver()
    assert len(minas) == 0
    assert len(seguras) == 0


if __name__ == '__main__':
    test_csp_resuelve_8_vecinas()
    test_bot_hace_movimiento()
    test_csp_sin_restricciones()
    print("Todos los tests de solver_csp pasaron.")
