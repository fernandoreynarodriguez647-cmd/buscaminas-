import random
import copy


class Board:
    def __init__(self, filas, columnas, num_minas):
        self.filas = filas
        self.columnas = columnas
        self.num_minas = num_minas
        self.estado = [['oculta' for _ in range(columnas)] for _ in range(filas)]
        self.minas = [[False for _ in range(columnas)] for _ in range(filas)]
        self.numeros = [[0 for _ in range(columnas)] for _ in range(filas)]
        self._colocar_minas()
        self._calcular_numeros()
        self.game_over = False
        self.won = False
        self.banderas_colocadas = 0
        self.descubiertas = 0
        self.minas_marcadas = 0

    def _colocar_minas(self):
        puestos = set()
        while len(puestos) < self.num_minas:
            f = random.randint(0, self.filas - 1)
            c = random.randint(0, self.columnas - 1)
            if (f, c) not in puestos:
                puestos.add((f, c))
                self.minas[f][c] = True

    def _calcular_numeros(self):
        for f in range(self.filas):
            for c in range(self.columnas):
                if self.minas[f][c]:
                    continue
                cont = 0
                for vf, vc in self._vecinos(f, c):
                    if self.minas[vf][vc]:
                        cont += 1
                self.numeros[f][c] = cont

    def _vecinos(self, f, c):
        result = []
        for df in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if df == 0 and dc == 0:
                    continue
                nf, nc = f + df, c + dc
                if 0 <= nf < self.filas and 0 <= nc < self.columnas:
                    result.append((nf, nc))
        return result

    def descubrir(self, f, c):
        if self.game_over or self.won:
            return
        if self.estado[f][c] != 'oculta':
            return
        if self.minas[f][c]:
            self.estado[f][c] = 'descubierta'
            self.game_over = True
            return
        self.estado[f][c] = 'descubierta'
        self.descubiertas += 1
        if self.numeros[f][c] == 0:
            for vf, vc in self._vecinos(f, c):
                if self.estado[vf][vc] == 'oculta':
                    self.descubrir(vf, vc)
        self._verificar_victoria()

    def marcar_bandera(self, f, c):
        if self.game_over or self.won:
            return
        if self.estado[f][c] == 'oculta':
            self.estado[f][c] = 'bandera'
            self.banderas_colocadas += 1
            if self.minas[f][c]:
                self.minas_marcadas += 1
        elif self.estado[f][c] == 'bandera':
            self.estado[f][c] = 'oculta'
            self.banderas_colocadas -= 1
            if self.minas[f][c]:
                self.minas_marcadas -= 1
        self._verificar_victoria()

    def _verificar_victoria(self):
        total_seguras = self.filas * self.columnas - self.num_minas
        if self.descubiertas >= total_seguras:
            self.won = True

    def minas_restantes(self):
        return self.num_minas - self.banderas_colocadas

    def obtener_casillas_frontera(self):
        frontera = set()
        for f in range(self.filas):
            for c in range(self.columnas):
                if self.estado[f][c] == 'oculta':
                    for vf, vc in self._vecinos(f, c):
                        if self.estado[vf][vc] == 'descubierta' and self.numeros[vf][vc] > 0:
                            frontera.add((f, c))
                            break
        return frontera

    def obtener_todas_ocultas(self):
        ocultas = set()
        for f in range(self.filas):
            for c in range(self.columnas):
                if self.estado[f][c] == 'oculta':
                    ocultas.add((f, c))
        return ocultas

    def clonar_para_bot(self):
        return copy.deepcopy(self)

    def __str__(self):
        lines = []
        for f in range(self.filas):
            line = ''
            for c in range(self.columnas):
                if self.estado[f][c] == 'oculta':
                    line += '? '
                elif self.estado[f][c] == 'bandera':
                    line += 'F '
                else:
                    if self.minas[f][c] and self.game_over:
                        line += 'X '
                    elif self.numeros[f][c] == 0:
                        line += '. '
                    else:
                        line += str(self.numeros[f][c]) + ' '
            lines.append(line)
        return '\n'.join(lines)
