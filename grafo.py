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

    def grado(self, nodo):
        """Devuelve el número total de conexiones (entrantes + salientes) del nodo."""
        entrantes = sum(1 for i in range(self.n) if self.matriz[i][nodo] != 0)
        salientes = sum(1 for j in range(self.n) if self.matriz[nodo][j] != 0)
        return entrantes + salientes

    def agregar_arista(self, origen, destino, peso):
        """
        Agrega una arista dirigida origen -> destino con el peso dado.
        Solo se permite si origen < destino, para garantizar que el
        grafo resultante sea acíclico por construcción.
        Además, limita a un máximo de 3 aristas totales por nodo.
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

        # Si no existe la arista, verificar que ninguno de los dos nodos supere las 3 conexiones
        if self.matriz[origen][destino] == 0:
            if self.grado(origen) >= 3:
                raise ValueError(f"El nodo {origen} ya tiene 3 conexiones (máximo permitido).")
            if self.grado(destino) >= 3:
                raise ValueError(f"El nodo {destino} ya tiene 3 conexiones (máximo permitido).")

        self.matriz[origen][destino] = peso

    def generar_aleatorio(self, densidad=0.4, peso_min=1, peso_max=20):
        """
        Genera un grafo aleatorio dirigido y acíclico asegurando que cada nodo
        tenga como mínimo 2 conexiones y como máximo 3 conexiones totales
        (aristas incidentes: entrantes + salientes entre 2 y 3).
        """
        self.limpiar()

        # Construcción inicial respetando el límite máximo de 3 conexiones por nodo
        pares = [(i, j) for i in range(self.n) for j in range(i + 1, self.n)]
        random.shuffle(pares)
        for i, j in pares:
            if random.random() < densidad:
                if self.grado(i) < 3 and self.grado(j) < 3:
                    self.matriz[i][j] = random.randint(peso_min, peso_max)

        # 1. Asegurar al menos una arista saliente (salvo el último nodo)
        for i in range(self.n - 1):
            salientes = sum(1 for j in range(i + 1, self.n) if self.matriz[i][j] != 0)
            if salientes == 0 and self.grado(i) < 3:
                candidatos = [j for j in range(i + 1, self.n) if self.matriz[i][j] == 0 and self.grado(j) < 3]
                if candidatos:
                    j = random.choice(candidatos)
                    self.matriz[i][j] = random.randint(peso_min, peso_max)

        # 2. Asegurar al menos una arista entrante (salvo el primer nodo)
        for j in range(1, self.n):
            entrantes = sum(1 for i in range(j) if self.matriz[i][j] != 0)
            if entrantes == 0 and self.grado(j) < 3:
                candidatos = [i for i in range(j) if self.matriz[i][j] == 0 and self.grado(i) < 3]
                if candidatos:
                    i = random.choice(candidatos)
                    self.matriz[i][j] = random.randint(peso_min, peso_max)

        # 3. Asegurar que ningún nodo quede con menos de 2 conexiones, sin superar 3
        for v in range(self.n):
            while self.grado(v) < 2:
                candidatos = []
                for u in range(v):
                    if self.matriz[u][v] == 0 and self.grado(u) < 3:
                        candidatos.append((u, v))
                for w in range(v + 1, self.n):
                    if self.matriz[v][w] == 0 and self.grado(w) < 3:
                        candidatos.append((v, w))

                if not candidatos:
                    break

                origen_nuevo, destino_nuevo = random.choice(candidatos)
                self.matriz[origen_nuevo][destino_nuevo] = random.randint(peso_min, peso_max)

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
