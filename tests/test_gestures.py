
from types import SimpleNamespace

from src.gesture_recognizer import GestureRecognizer


def crear_mano(dedos_levantados):
    """
    Crea una mano simulada con 21 puntos.
    No necesita una camara real.
    """
    puntos = [
        SimpleNamespace(x=0.5, y=0.5)
        for _ in range(21)
    ]

    pares = [
        (8, 6),
        (12, 10),
        (16, 14),
        (20, 18),
    ]

    for levantado, (yema, articulacion) in zip(
        dedos_levantados, pares
    ):
        puntos[articulacion].y = 0.5

        if levantado:
            puntos[yema].y = 0.3
        else:
            puntos[yema].y = 0.7

    return SimpleNamespace(landmark=puntos)


def test_reconocer_gesto_dibujar():
    # ARRANGE: Preparar una mano con solo
    # el dedo indice levantado.
    reconocedor = GestureRecognizer()
    mano = crear_mano([True, False, False, False])

    # ACT: Ejecutar el reconocimiento.
    resultado = reconocedor.reconocer(mano)

    # ASSERT: Comprobar el resultado.
    assert resultado == "DIBUJAR"


def test_reconocer_gesto_pausa():
    # ARRANGE: Indice y medio levantados.
    reconocedor = GestureRecognizer()
    mano = crear_mano([True, True, False, False])

    # ACT
    resultado = reconocedor.reconocer(mano)

    # ASSERT
    assert resultado == "PAUSA"


def test_reconocer_gesto_puno():
    # ARRANGE: Todos los dedos cerrados.
    reconocedor = GestureRecognizer()
    mano = crear_mano([False, False, False, False])

    # ACT
    resultado = reconocedor.reconocer(mano)

    # ASSERT
    assert resultado == "PUNO"


def test_reconocer_mano_abierta():
    # ARRANGE: Cuatro dedos levantados.
    reconocedor = GestureRecognizer()
    mano = crear_mano([True, True, True, True])

    # ACT
    resultado = reconocedor.reconocer(mano)

    # ASSERT
    assert resultado == "MANO_ABIERTA"


def test_reconocer_sin_mano():
    # ARRANGE: No se detecta ninguna mano.
    reconocedor = GestureRecognizer()

    # ACT
    resultado = reconocedor.reconocer(None)

    # ASSERT
    assert resultado == "SIN_MANO"


def test_reconocer_gesto_desconocido():
    # ARRANGE: Combinacion no configurada.
    reconocedor = GestureRecognizer()
    mano = crear_mano([True, False, True, False])

    # ACT
    resultado = reconocedor.reconocer(mano)

    # ASSERT
    assert resultado == "DESCONOCIDO"


def test_detectar_pinza():
    # ARRANGE: Pulgar e indice cercanos.
    reconocedor = GestureRecognizer()
    mano = crear_mano([True, False, False, False])

    mano.landmark[4].x = 0.50
    mano.landmark[4].y = 0.30

    mano.landmark[8].x = 0.51
    mano.landmark[8].y = 0.31

    # ACT
    resultado = reconocedor.es_pinza(mano)

    # ASSERT
    assert resultado is True


def test_no_detectar_pinza():
    # ARRANGE: Pulgar e indice separados.
    reconocedor = GestureRecognizer()
    mano = crear_mano([True, False, False, False])

    mano.landmark[4].x = 0.20
    mano.landmark[4].y = 0.20

    mano.landmark[8].x = 0.80
    mano.landmark[8].y = 0.30

    # ACT
    resultado = reconocedor.es_pinza(mano)

    # ASSERT
    assert resultado is False
