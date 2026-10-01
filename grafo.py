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
        Genera un grafo aleatorio dirigido y acíclico.

        Se recorren únicamente los pares (i, j) con i < j, de modo que
        toda arista generada respeta el orden de índices y el grafo
        queda garantizado como acíclico sin necesidad de validación
        adicional.

        densidad: probabilidad de que exista una arista entre cada
                  par válido (i, j).
        """
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if random.random() < densidad:
                    peso = random.randint(peso_min, peso_max)
                    self.matriz[i][j] = peso

        # Aseguramos que cada nodo (salvo el último) tenga al menos
        # una arista saliente, para evitar nodos totalmente aislados
        # al inicio del grafo.
        for i in range(self.n - 1):
            if all(self.matriz[i][j] == 0 for j in range(i + 1, self.n)):
                j = random.randint(i + 1, self.n - 1)
                self.matriz[i][j] = random.randint(peso_min, peso_max)

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