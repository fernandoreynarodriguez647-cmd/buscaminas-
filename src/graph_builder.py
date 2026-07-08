import networkx as nx


def obtener_restricciones(board):
    restricciones = {}
    for f in range(board.filas):
        for c in range(board.columnas):
            if board.estado[f][c] == 'descubierta' and board.numeros[f][c] > 0:
                vecinas_ocultas = set()
                for vf, vc in board._vecinos(f, c):
                    if board.estado[vf][vc] == 'oculta':
                        vecinas_ocultas.add((vf, vc))
                if vecinas_ocultas:
                    restricciones[(f, c)] = {
                        'valor': board.numeros[f][c],
                        'vecinas_ocultas': vecinas_ocultas
                    }
    return restricciones


def build_constraint_graph(board):
    restricciones = obtener_restricciones(board)
    grafo = nx.Graph()
    for restriccion in restricciones.values():
        nodos = list(restriccion['vecinas_ocultas'])
        grafo.add_nodes_from(nodos)
        for i in range(len(nodos)):
            for j in range(i + 1, len(nodos)):
                grafo.add_edge(nodos[i], nodos[j])
    return grafo
