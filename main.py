from src.board import Board
from src.graph_builder import build_constraint_graph
from src.graph_analysis import particionar_tablero
from src.visualizer import dibujar_grafo


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


if __name__ == '__main__':
    main()
