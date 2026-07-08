import random
from collections import defaultdict
from src.graph_builder import obtener_restricciones, build_constraint_graph
from src.graph_analysis import obtener_componentes


class MinesweeperCSP:
    def __init__(self, board):
        self.board = board
        self.known_mines = set()
        self.known_safe = set()

    def resolver(self):
        restricciones = obtener_restricciones(self.board)
        if not restricciones:
            return set(), set()
        grafo = build_constraint_graph(self.board)
        componentes = obtener_componentes(grafo)
        minas = set()
        seguras = set()
        for comp in componentes:
            restricciones_comp = {}
            for pos, restr in restricciones.items():
                if restr['vecinas_ocultas'] & comp:
                    restricciones_comp[pos] = restr
            m, s = self._resolver_componente(restricciones_comp, comp)
            minas.update(m)
            seguras.update(s)
        return minas, seguras

    def _resolver_componente(self, restricciones, nodos):
        minas = set()
        seguras = set()
        if not restricciones:
            return minas, seguras
        nodos_lista = list(nodos)
        restricciones_lista = []
        for pos, restr in restricciones.items():
            restricciones_lista.append({
                'pos': pos,
                'valor': restr['valor'],
                'nodos': restr['vecinas_ocultas']
            })
        cambio = True
        while cambio:
            cambio = False
            for restr in restricciones_lista:
                vecinas = restr['nodos'] - minas - seguras
                valor = restr['valor'] - len(restr['nodos'] & minas)
                minas_marcadas = len(restr['nodos'] & minas)
                if len(vecinas) == 0:
                    continue
                if valor == 0:
                    for v in vecinas:
                        if v not in seguras:
                            seguras.add(v)
                            cambio = True
                elif len(vecinas) == valor:
                    for v in vecinas:
                        if v not in minas:
                            minas.add(v)
                            cambio = True
        if not minas and not seguras:
            mina_azar = self._elegir_menos_riesgoso(nodos_lista, restricciones_lista)
            if mina_azar:
                seguras.add(mina_azar)
        return minas, seguras

    def _elegir_menos_riesgoso(self, nodos, restricciones):
        if not nodos:
            return None
        riesgo = {n: 0 for n in nodos}
        for restr in restricciones:
            vecinas = restr['nodos'] - self.known_mines - self.known_safe
            if len(vecinas) == 0:
                continue
            prob = restr['valor'] / len(vecinas)
            for v in vecinas:
                riesgo[v] = max(riesgo[v], prob)
        if all(r == 0 for r in riesgo.values()):
            for n in nodos:
                riesgo[n] = 1
        min_riesgo = min(riesgo.values())
        candidatos = [n for n, r in riesgo.items() if r == min_riesgo]
        return random.choice(candidatos)


class BotJugador:
    def __init__(self, board):
        self.board = board
        self.csp = MinesweeperCSP(board)

    def jugar_turno(self):
        if self.board.game_over or self.board.won:
            return
        minas, seguras = self.csp.resolver()
        if seguras:
            f, c = next(iter(seguras))
            if not self.board.minas[f][c]:
                self.board.descubrir(f, c)
                return ('descubrir', (f, c))
        if minas:
            for m in minas:
                if m not in self.board.obtener_casillas_frontera():
                    continue
                if self.board.estado[m[0]][m[1]] == 'oculta':
                    self.board.marcar_bandera(m[0], m[1])
                    return ('marcar', m)
        frontera = self.board.obtener_casillas_frontera()
        if frontera:
            f, c = random.choice(list(frontera))
            if not self.board.minas[f][c]:
                self.board.descubrir(f, c)
                return ('descubrir', (f, c))
        ocultas = self.board.obtener_todas_ocultas()
        if ocultas:
            f, c = random.choice(list(ocultas))
            if not self.board.minas[f][c]:
                self.board.descubrir(f, c)
                return ('descubrir', (f, c))
        return ('nada', None)
