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

    def agregar_arista(self, origen, destino, peso):
        """
        Agrega una arista dirigida origen -> destino con el peso dado.
        Solo se permite si origen < destino, para garantizar que el
        grafo resultante sea acíclico por construcción.
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

        self.matriz[origen][destino] = peso

    def generar_aleatorio(self, densidad=0.4, peso_min=1, peso_max=20):
        """
        Genera un grafo aleatorio dirigido y acíclico asegurando que cada nodo
        tenga al menos 2 conexiones (grado total: entrantes + salientes >= 2,
        siempre que la estructura acíclica lo permita).
        """
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if random.random() < densidad:
                    peso = random.randint(peso_min, peso_max)
                    self.matriz[i][j] = peso

        # Garantizar mínimo 2 conexiones por nodo (entrantes + salientes)
        for v in range(self.n):
            while True:
                # Contar grado total del nodo v
                entrantes = sum(1 for u in range(self.n) if self.matriz[u][v] != 0)
                salientes = sum(1 for w in range(self.n) if self.matriz[v][w] != 0)
                grado_total = entrantes + salientes

                if grado_total >= 2:
                    break

                # Si le faltan conexiones, intentamos agregar una arista válida
                if salientes < 1 and v < self.n - 1:
                    w = random.randint(v + 1, self.n - 1)
                    if self.matriz[v][w] == 0:
                        self.matriz[v][w] = random.randint(peso_min, peso_max)
                        continue
                if entrantes < 1 and v > 0:
                    u = random.randint(0, v - 1)
                    if self.matriz[u][v] == 0:
                        self.matriz[u][v] = random.randint(peso_min, peso_max)
                        continue
                break

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