"""
Módulo: dijkstra.py
Implementación del algoritmo de Dijkstra sobre un grafo representado
mediante matriz de adyacencia, con seguimiento del estado en cada
iteración (para poder mostrar la ejecución paso a paso) y con soporte
para identificar TODOS los caminos mínimos entre el vértice origen y
el vértice destino.

Curso: 1AMA0726 - Matemática Computacional
Proyecto: Problema del camino mínimo (algoritmo de Dijkstra)
"""

INFINITO = float("inf")


class PasoDijkstra:
    """
    Representa el estado del algoritmo después de una iteración.
    Se usa para mostrar la ejecución paso a paso en la interfaz.
    """

    def __init__(self, iteracion, nodo_actual, distancias, visitados, actualizaciones):
        self.iteracion = iteracion
        self.nodo_actual = nodo_actual
        # Copia de las distancias en este momento de la ejecución
        self.distancias = list(distancias)
        # Copia del conjunto de nodos visitados hasta este momento
        self.visitados = list(visitados)
        # Lista de tuplas (vecino, distancia_anterior, distancia_nueva)
        # que indican qué distancias se actualizaron en esta iteración
        self.actualizaciones = actualizaciones


def ejecutar_dijkstra(grafo, origen):
    """
    Ejecuta el algoritmo de Dijkstra desde 'origen' sobre todo el grafo.

    Devuelve:
        distancias: lista con la distancia mínima desde 'origen' a cada
                    vértice (INFINITO si no es alcanzable).
        predecesores: lista de listas; predecesores[v] contiene todos los
                    vértices u tales que la arista (u, v) forma parte de
                    al menos un camino mínimo hacia v. Puede tener más de
                    un elemento cuando existen múltiples caminos mínimos.
        pasos: lista de objetos PasoDijkstra, uno por cada iteración,
               para reproducir la ejecución paso a paso en la interfaz.
    """
    n = grafo.n
    distancias = [INFINITO] * n
    distancias[origen] = 0
    visitados = [False] * n
    predecesores = [[] for _ in range(n)]

    pasos = []
    iteracion = 0

    while True:
        # Paso 1: seleccionar, entre los vértices no visitados, el de
        # menor distancia acumulada.
        actual = None
        menor_distancia = INFINITO
        for v in range(n):
            if not visitados[v] and distancias[v] < menor_distancia:
                menor_distancia = distancias[v]
                actual = v

        # Si no queda ningún vértice alcanzable, termina la ejecución.
        if actual is None:
            break

        visitados[actual] = True
        iteracion += 1
        actualizaciones = []

        # Paso 2: actualizar las distancias de los vecinos de 'actual'.
        for vecino in grafo.vecinos(actual):
            if visitados[vecino]:
                continue
            peso = grafo.matriz[actual][vecino]
            nueva_distancia = distancias[actual] + peso

            if nueva_distancia < distancias[vecino]:
                # Se encontró un camino estrictamente más corto: se
                # reemplaza el/los predecesor(es) anterior(es).
                anterior = distancias[vecino]
                distancias[vecino] = nueva_distancia
                predecesores[vecino] = [actual]
                actualizaciones.append((vecino, anterior, nueva_distancia))

            elif nueva_distancia == distancias[vecino] and nueva_distancia != INFINITO:
                # Se encontró OTRO camino con la MISMA distancia mínima:
                # se agrega 'actual' como predecesor adicional, sin
                # modificar la distancia ya registrada.
                if actual not in predecesores[vecino]:
                    predecesores[vecino].append(actual)
                    actualizaciones.append((vecino, distancias[vecino], distancias[vecino]))

        pasos.append(PasoDijkstra(iteracion, actual, distancias, visitados, actualizaciones))

    return distancias, predecesores, pasos


def reconstruir_caminos(predecesores, origen, destino):
    """
    Reconstruye TODOS los caminos mínimos desde 'origen' hasta 'destino'
    a partir de la lista de predecesores, mediante backtracking
    (recorrido hacia atrás) desde el destino hasta el origen.

    Devuelve una lista de caminos; cada camino es una lista de vértices
    en el orden origen -> ... -> destino.
    """
    caminos = []

    def backtrack(nodo, camino_parcial):
        if nodo == origen:
            caminos.append([origen] + camino_parcial)
            return
        for pred in predecesores[nodo]:
            backtrack(pred, [nodo] + camino_parcial)

    backtrack(destino, [])
    return caminos