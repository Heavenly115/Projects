import cv2
import numpy as np
from datetime import datetime
from pathlib import Path


class CanvasController:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto

        self.lienzo = np.zeros(
            (alto, ancho, 3),
            dtype=np.uint8
        )

        self.mascara = np.zeros(
            (alto, ancho),
            dtype=np.uint8
        )

        # Guardar un punto anterior para cada mano
        self.puntos_anteriores = {}

        # Colores en formato BGR
        self.colores = {
            "Left": (255, 0, 255),    # Morado
            "Right": (0, 255, 255),   # Amarillo
        }

        self.grosor = 5

    def dibujar(self, punto, mano_id):
        anterior = self.puntos_anteriores.get(mano_id)

        if anterior is not None:
            color = self.colores.get(
                mano_id, (255, 255, 255)
            )

            cv2.line(
                self.lienzo,
                anterior,
                punto,
                color,
                self.grosor
            )

            cv2.line(
                self.mascara,
                anterior,
                punto,
                255,
                self.grosor
            )

        self.puntos_anteriores[mano_id] = punto

    def dibujar_figura(self, figura, inicio, fin):
        figura.dibujar(
            self.lienzo,
            inicio,
            fin
        )

        mascara_temporal = np.zeros_like(self.lienzo)

        figura.dibujar(
            mascara_temporal,
            inicio,
            fin
        )

        pixeles = np.any(
            mascara_temporal != 0,
            axis=2
        )

        self.mascara[pixeles] = 255

    def pausar(self, mano_id=None):
        if mano_id is None:
            self.puntos_anteriores.clear()
        else:
            self.puntos_anteriores.pop(mano_id, None)

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