import numpy as np

from src.drawing import (
    Linea,
    Rectangulo,
    Circulo,
    Triangulo
)


def crear_lienzo():
    return np.zeros((400, 600, 3), dtype=np.uint8)


def test_linea():
    lienzo = crear_lienzo()

    Linea().dibujar(lienzo, (50, 50), (200, 200))

    assert np.any(lienzo != 0)


def test_rectangulo():
    lienzo = crear_lienzo()

    Rectangulo().dibujar(lienzo, (50, 50), (200, 200))

    assert np.any(lienzo != 0)


def test_circulo():
    lienzo = crear_lienzo()

    Circulo().dibujar(lienzo, (150, 150), (200, 150))

    assert np.any(lienzo != 0)


def test_triangulo():
    lienzo = crear_lienzo()

    Triangulo().dibujar(lienzo, (50, 50), (200, 200))

    assert np.any(lienzo != 0)