import cv2
import numpy as np


class Figura:
    def __init__(self, color=(255, 0, 255), grosor=3):
        self.color = color
        self.grosor = grosor

    def dibujar(self, lienzo, inicio, fin):
        raise NotImplementedError(
            "Cada figura debe implementar el método dibujar"
        )


class Linea(Figura):
    def dibujar(self, lienzo, inicio, fin):
        cv2.line(
            lienzo,
            inicio,
            fin,
            self.color,
            self.grosor
        )


class Rectangulo(Figura):
    def dibujar(self, lienzo, inicio, fin):
        cv2.rectangle(
            lienzo,
            inicio,
            fin,
            self.color,
            self.grosor
        )


class Circulo(Figura):
    def dibujar(self, lienzo, inicio, fin):
        radio = int(
            np.hypot(
                fin[0] - inicio[0],
                fin[1] - inicio[1]
            )
        )

        cv2.circle(
            lienzo,
            inicio,
            radio,
            self.color,
            self.grosor
        )


class Triangulo(Figura):
    def dibujar(self, lienzo, inicio, fin):
        x1, y1 = inicio
        x2, y2 = fin

        puntos = np.array(
            [
                [(x1 + x2) // 2, y1],
                [x1, y2],
                [x2, y2]
            ],
            dtype=np.int32
        )

        cv2.polylines(
            lienzo,
            [puntos],
            isClosed=True,
            color=self.color,
            thickness=self.grosor
        )