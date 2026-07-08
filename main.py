from src.board import Board
from src.graph_builder import build_constraint_graph
from src.graph_analysis import particionar_tablero, metricas_grafo
from src.visualizer import dibujar_grafo
from src.solver_csp import BotJugador


def demo_bot():
    print("=== DEMO BOT JUGANDO ===")
    board = Board(9, 9, 10)
    board.descubrir(4, 4)
    bot = BotJugador(board)
    movidas = 0
    while not board.game_over and not board.won and movidas < 200:
        accion, pos = bot.jugar_turno()
        movidas += 1
        if pos:
            f, c = pos
            if accion == 'descubrir':
                pass
            elif accion == 'marcar':
                pass
    if board.won:
        print(f"Bot ganó en {movidas} movidas")
    else:
        print(f"Bot perdió después de {movidas} movidas")
    print(f"Tablero final:\n{board}")
    return board


def main():
    tablero = Board(9, 9, 10)
    tablero.descubrir(4, 4)

    print("=== TABLERO ===")
    print(tablero)
    print()

    grafo = build_constraint_graph(tablero)
    print(f"=== GRAFO DE RESTRICCIONES ===")
    print(f"Nodos: {grafo.number_of_nodes()}")
    print(f"Aristas: {grafo.number_of_edges()}")

    met = metricas_grafo(grafo)
    print(f"Componentes: {met['componentes']}")
    print(f"Densidad: {met['densidad']:.3f}")
    print(f"Grado promedio: {met['grado_promedio']:.2f}")
    print(f"Comp. más grande: {met['componente_mas_grande']}")
    print()

    subproblemas = particionar_tablero(tablero)
    print(f"=== COMPONENTES ===")
    print(f"Cantidad de componentes: {len(subproblemas)}")
    for i, sp in enumerate(subproblemas):
        print(f"  Componente {i+1}: {len(sp['nodos'])} casillas, {len(sp['restricciones'])} restricciones")
        print(f"    Casillas: {sorted(sp['nodos'])}")
    print()

    print("Dibujando grafo...")
    componentes = [sp['nodos'] for sp in subproblemas]
    dibujar_grafo(grafo, componentes)

    print()
    tablero_bot = demo_bot()


if __name__ == '__main__':
    main()
