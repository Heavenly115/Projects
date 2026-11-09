import cv2
import numpy as np
from datetime import datetime
from pathlib import Path


class CanvasController:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto

        # Lienzo transparente representado mediante una máscara
        self.lienzo = np.zeros(
            (alto, ancho, 3),
            dtype=np.uint8
        )

        self.mascara = np.zeros(
            (alto, ancho),
            dtype=np.uint8
        )

        self.punto_anterior = None
        self.color = (255, 0, 255)  # Morado en formato BGR
        self.grosor = 5

    def dibujar(self, punto):
        if self.punto_anterior is not None:
            cv2.line(
                self.lienzo,
                self.punto_anterior,
                punto,
                self.color,
                self.grosor
            )

            cv2.line(
                self.mascara,
                self.punto_anterior,
                punto,
                255,
                self.grosor
            )

        self.punto_anterior = punto

    def pausar(self):
        self.punto_anterior = None

    def limpiar(self):
        self.lienzo.fill(0)
        self.mascara.fill(0)
        self.pausar()

    def combinar(self, frame):
        resultado = frame.copy()

        resultado[self.mascara > 0] = (
            self.lienzo[self.mascara > 0]
        )

        return resultado

    def guardar(self):
        carpeta = Path("dibujos")
        carpeta.mkdir(exist_ok=True)

        nombre = datetime.now().strftime(
            "dibujo_%Y%m%d_%H%M%S_%f.png"
        )

        ruta = carpeta / nombre

        # Guardar el dibujo sobre un fondo blanco
        imagen = np.full(
            (self.alto, self.ancho, 3),
            255,
            dtype=np.uint8
        )

        imagen[self.mascara > 0] = (
            self.lienzo[self.mascara > 0]
        )

        if not cv2.imwrite(str(ruta), imagen):
            raise OSError("No se pudo guardar el dibujo")

        return ruta