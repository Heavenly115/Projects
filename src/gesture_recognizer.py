import math


class GestureRecognizer:
    def dedos_levantados(self, mano):
        if mano is None:
            return [False, False, False, False]

        puntos = mano.landmark
        pares = [(8, 6), (12, 10), (16, 14), (20, 18)]

        return [
            puntos[yema].y < puntos[articulacion].y
            for yema, articulacion in pares
        ]

    def es_pinza(self, mano, umbral=0.055):
        if mano is None:
            return False

        pulgar = mano.landmark[4]
        indice = mano.landmark[8]

        distancia = math.hypot(
            pulgar.x - indice.x,
            pulgar.y - indice.y
        )

        return distancia < umbral

    def reconocer(self, mano):
        if mano is None:
            return "SIN_MANO"

        dedos = self.dedos_levantados(mano)

        if dedos == [True, False, False, False]:
            return "DIBUJAR"

        if dedos == [True, True, False, False]:
            return "PAUSA"

        if dedos == [False, False, False, False]:
            return "PUNO"

        if dedos == [True, True, True, True]:
            return "MANO_ABIERTA"

        return "DESCONOCIDO"