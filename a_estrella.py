from heapq import heappop, heappush


def distancia_manhattan(origen, destino):
    fila, columna = origen
    fila_meta, columna_meta = destino
    return abs(fila_meta - fila) + abs(columna_meta - columna)


def vecinos(posicion, mapa):
    fila, columna = posicion

    for df, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nueva_fila = fila + df
        nueva_columna = columna + dc

        dentro = (
            0 <= nueva_fila < len(mapa)
            and 0 <= nueva_columna < len(mapa[0])
        )

        if dentro and mapa[nueva_fila][nueva_columna] == 0:
            yield nueva_fila, nueva_columna


def reconstruir(padres, destino):
    ruta = []
    paso = destino

    while paso is not None:
        ruta.append(paso)
        paso = padres[paso]

    ruta.reverse()
    return ruta


def a_estrella(mapa, inicio, destino):
    # Comprobar que inicio y destino sean casillas transitables.
    for fila, columna in (inicio, destino):
        if not (
            0 <= fila < len(mapa)
            and 0 <= columna < len(mapa[0])
        ):
            raise ValueError("Inicio o destino fuera del mapa.")

        if mapa[fila][columna] != 0:
            raise ValueError("Inicio o destino sobre un obstáculo.")

    # Cada entrada contiene: (prioridad f, costo g, posición).
    pendientes = [(distancia_manhattan(inicio, destino), 0, inicio)]
    costos = {inicio: 0}
    padres = {inicio: None}

    while pendientes:
        _, costo_actual, posicion = heappop(pendientes)

        # Ignorar entradas antiguas si ya existe una ruta mejor.
        if costo_actual > costos[posicion]:
            continue

        if posicion == destino:
            return reconstruir(padres, destino)

        for siguiente in vecinos(posicion, mapa):
            costo_nuevo = costo_actual + 1

            if costo_nuevo >= costos.get(siguiente, float("inf")):
                continue

            costos[siguiente] = costo_nuevo
            padres[siguiente] = posicion

            estimacion = distancia_manhattan(siguiente, destino)
            prioridad = costo_nuevo + estimacion
            heappush(pendientes, (prioridad, costo_nuevo, siguiente))

    return None


def mostrar_mapa(mapa, ruta, inicio, destino):
    recorrido = set(ruta or [])

    for fila, valores in enumerate(mapa):
        simbolos = []

        for columna, valor in enumerate(valores):
            posicion = (fila, columna)

            if posicion == inicio:
                simbolo = "I"
            elif posicion == destino:
                simbolo = "F"
            elif valor == 1:
                simbolo = "#"
            elif posicion in recorrido:
                simbolo = "*"
            else:
                simbolo = "."

            simbolos.append(simbolo)

        print(" ".join(simbolos))


if __name__ == "__main__":
    # 0 = casilla libre; 1 = obstáculo.
    mapa = [
        [0, 0, 0, 0, 0],
        [1, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ]

    inicio = (0, 0)
    destino = (4, 4)

    ruta = a_estrella(mapa, inicio, destino)

    if ruta is None:
        print("No existe un camino.")
    else:
        print("Camino encontrado:", ruta)
        print("Costo total:", len(ruta) - 1)

    print("\nI: inicio | F: destino | #: obstáculo | *: camino\n")
    mostrar_mapa(mapa, ruta, inicio, destino)