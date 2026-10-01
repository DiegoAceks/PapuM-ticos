"""
Módulo: conectividad.py
Verificación de conectividad entre dos vértices mediante búsqueda de
componentes conexas sobre el grafo no dirigido subyacente.

Curso: 1AMA0726 - Matemática Computacional
"""


def existe_camino(grafo, origen, destino):
    """
    Determina si existe al menos un camino entre 'origen' y 'destino',
    ignorando la dirección de las aristas (es decir, verifica si ambos
    nodos pertenecen a la misma componente conexa del grafo no dirigido
    subyacente).

    Se usa una búsqueda en anchura (BFS) simple, recorriendo tanto las
    aristas salientes como entrantes de cada nodo.
    """
    n = grafo.n
    visitados = [False] * n
    cola = [origen]
    visitados[origen] = True

    while cola:
        actual = cola.pop(0)
        if actual == destino:
            return True

        for j in range(n):
            conectado = grafo.matriz[actual][j] != 0 or grafo.matriz[j][actual] != 0
            if conectado and not visitados[j]:
                visitados[j] = True
                cola.append(j)

    return visitados[destino]