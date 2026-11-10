from datetime import datetime
from pathlib import Path

import cv2
import numpy as np


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

        # Cada mano tiene su propio punto anterior.
        self.puntos_anteriores = {}

        # Paleta en formato BGR de OpenCV.
        self.paleta = {
            "MORADO": (255, 0, 255),
            "ROJO": (0, 0, 255),
            "VERDE": (0, 255, 0),
            "AZUL": (255, 0, 0),
            "AMARILLO": (0, 255, 255),
            "BLANCO": (255, 255, 255)
        }

        # Colores independientes por mano.
        self.colores_manos = {
            "Left": "ROJO",
            "Right": "AZUL"
        }

        # Mano cuyo color se modificará con el teclado.
        self.mano_seleccionada = "Left"

        self.grosor = 5
        self.grosor_borrador = 35
        self.modo_borrador = False

    def seleccionar_mano(self, mano_id):
        if mano_id not in self.colores_manos:
            raise ValueError("Mano no disponible")

        self.mano_seleccionada = mano_id

    def cambiar_color(self, nombre):
        if nombre not in self.paleta:
            raise ValueError("Color no disponible")

        self.colores_manos[self.mano_seleccionada] = nombre

        # Cambiar color desactiva el borrador.
        self.modo_borrador = False
        self.pausar()

    def obtener_color(self, mano_id):
        nombre = self.colores_manos.get(
            mano_id,
            "MORADO"
        )

        return self.paleta[nombre]

    def activar_borrador(self):
        self.modo_borrador = True
        self.pausar()

    def cambiar_grosor(self, grosor):
        self.grosor = max(
            1,
            min(30, grosor)
        )
        self.pausar()

    def dibujar(self, punto, mano_id):
        anterior = self.puntos_anteriores.get(mano_id)

        if anterior is not None:
            if self.modo_borrador:
                # Quitar píxeles de la máscara.
                cv2.line(
                    self.mascara,
                    anterior,
                    punto,
                    0,
                    self.grosor_borrador
                )
            else:
                color = self.obtener_color(mano_id)

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

    def dibujar_figura(
        self,
        figura,
        inicio,
        fin,
        mano_id
    ):
        figura.color = self.obtener_color(mano_id)
        figura.grosor = self.grosor

        figura.dibujar(
            self.lienzo,
            inicio,
            fin
        )

        mascara_temporal = np.zeros_like(
            self.lienzo
        )

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
            self.puntos_anteriores.pop(
                mano_id,
                None
            )

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
            raise OSError(
                "No se pudo guardar el dibujo"
            )

        return ruta