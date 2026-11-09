"""
Módulo: grafo.py
Representación del grafo mediante matriz de adyacencia y funciones
para su construcción manual o aleatoria.

Curso: 1AMA0726 - Matemática Computacional
Proyecto: Problema del camino mínimo (algoritmo de Dijkstra)
"""

import random


class Grafo:
    """
    Representa un grafo dirigido y acíclico mediante una matriz de
    adyacencia de tamaño n x n.

    matriz[i][j] = peso de la arista i -> j
    matriz[i][j] = 0 significa que no existe arista entre i y j.
    """

    def __init__(self, n):
        if n < 7 or n > 16:
            raise ValueError("El número de nodos n debe estar entre 7 y 16.")
        self.n = n
        self.matriz = [[0 for _ in range(n)] for _ in range(n)]

    def grado_total(self, nodo):
        """Devuelve el total absoluto de aristas conectadas al nodo (entrantes + salientes)."""
        entrantes = sum(1 for i in range(self.n) if self.matriz[i][nodo] != 0)
        salientes = sum(1 for j in range(self.n) if self.matriz[nodo][j] != 0)
        return entrantes + salientes

    def agregar_arista(self, origen, destino, peso):
        """
        Agrega una arista dirigida origen -> destino con el peso dado.
        Solo se permite si origen < destino, para garantizar que el
        grafo resultante sea acíclico por construcción.
        Además, limita a un total máximo de 3 aristas por nodo (entrantes + salientes <= 3).
        """
        if origen == destino:
            raise ValueError("No se permiten auto-ciclos (origen == destino).")
        if origen >= destino:
            raise ValueError(
                "Para garantizar un grafo dirigido y acíclico, la arista "
                "debe ir de un nodo con índice menor a uno con índice mayor "
                f"(se recibió {origen} -> {destino})."
            )
        if peso <= 0:
            raise ValueError("El peso de la arista debe ser un número positivo.")

        # Si no existe la arista, verificar que ningún nodo supere las 3 conexiones totales
        if self.matriz[origen][destino] == 0:
            if self.grado_total(origen) >= 3:
                raise ValueError(f"El nodo {origen} ya tiene 3 aristas conectadas en total (máximo permitido: 3).")
            if self.grado_total(destino) >= 3:
                raise ValueError(f"El nodo {destino} ya tiene 3 aristas conectadas en total (máximo permitido: 3).")

        self.matriz[origen][destino] = peso

    def generar_aleatorio(self, densidad=0.4, peso_min=1, peso_max=20):
        """
        Genera un grafo aleatorio dirigido y acíclico asegurando que:
        - Cada nodo tenga como MÍNIMO 2 aristas totales conectadas.
        - Cada nodo tenga como MÁXIMO 3 aristas totales conectadas (entrantes + salientes <= 3).
        """
        for intento in range(500):
            self.limpiar()

            # 1. Asegurar al menos una arista saliente para cada nodo (salvo el último)
            for i in range(self.n - 1):
                posibles = [j for j in range(i + 1, self.n) if self.grado_total(j) < 3]
                if posibles and self.grado_total(i) < 3:
                    j = random.choice(posibles)
                    self.matriz[i][j] = random.randint(peso_min, peso_max)

            # 2. Asegurar al menos una arista entrante para cada nodo (salvo el primero)
            for j in range(1, self.n):
                entrantes = sum(1 for i in range(j) if self.matriz[i][j] != 0)
                if entrantes == 0 and self.grado_total(j) < 3:
                    posibles = [i for i in range(j) if self.grado_total(i) < 3]
                    if posibles:
                        i = random.choice(posibles)
                        self.matriz[i][j] = random.randint(peso_min, peso_max)

            # 3. Agregar aristas adicionales según densidad respetando el tope total <= 3
            pares = [
                (i, j) for i in range(self.n) for j in range(i + 1, self.n)
                if self.matriz[i][j] == 0
            ]
            random.shuffle(pares)
            for i, j in pares:
                if random.random() < densidad:
                    if self.grado_total(i) < 3 and self.grado_total(j) < 3:
                        self.matriz[i][j] = random.randint(peso_min, peso_max)

            # 4. Asegurar que ningún nodo quede con menos de 2 conexiones totales
            for v in range(self.n):
                while self.grado_total(v) < 2:
                    cands = []
                    for u in range(v):
                        if self.matriz[u][v] == 0 and self.grado_total(u) < 3:
                            cands.append((u, v))
                    for w in range(v + 1, self.n):
                        if self.matriz[v][w] == 0 and self.grado_total(w) < 3:
                            cands.append((v, w))
                    if not cands:
                        break
                    u_sel, w_sel = random.choice(cands)
                    self.matriz[u_sel][w_sel] = random.randint(peso_min, peso_max)

            # 5. Validar que cumpla todas las restricciones estrictamente
            valido = True
            for v in range(self.n):
                gt = self.grado_total(v)
                salientes = sum(1 for j in range(v + 1, self.n) if self.matriz[v][j] != 0)
                entrantes = sum(1 for i in range(v) if self.matriz[i][v] != 0)

                if gt < 2 or gt > 3:
                    valido = False
                    break
                if v < self.n - 1 and salientes == 0:
                    valido = False
                    break
                if v > 0 and entrantes == 0:
                    valido = False
                    break

            if valido:
                return

    def obtener_aristas(self):
        """Devuelve una lista de tuplas (origen, destino, peso)."""
        aristas = []
        for i in range(self.n):
            for j in range(self.n):
                if self.matriz[i][j] != 0:
                    aristas.append((i, j, self.matriz[i][j]))
        return aristas

    def vecinos(self, nodo):
        """Devuelve la lista de nodos alcanzables directamente desde 'nodo'."""
        return [j for j in range(self.n) if self.matriz[nodo][j] != 0]

    def eliminar_arista(self, origen, destino):
        """Elimina la arista origen -> destino, si existe."""
        self.matriz[origen][destino] = 0

    def limpiar(self):
        """Elimina todas las aristas, dejando la matriz en ceros."""
        self.matriz = [[0 for _ in range(self.n)] for _ in range(self.n)]
