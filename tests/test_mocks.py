
from types import SimpleNamespace

import numpy as np

from src.hand_detector import HandDetector


class DetectorSimulado:
    """
    Simula el resultado de MediaPipe.

    No necesita una camara ni una mano real.
    """

    def process(self, imagen):
        puntos = [
            SimpleNamespace(x=0.5, y=0.5, z=0.0)
            for _ in range(21)
        ]

        mano = SimpleNamespace(
            landmark=puntos
        )

        clasificacion = SimpleNamespace(
            label="Right"
        )

        handedness = SimpleNamespace(
            classification=[clasificacion]
        )

        return SimpleNamespace(
            multi_hand_landmarks=[mano],
            multi_handedness=[handedness],
        )


def test_deteccion_con_monkeypatch(monkeypatch):
    # ARRANGE:
    # Crear una imagen simulada.
    imagen = np.zeros(
        (480, 640, 3),
        dtype=np.uint8,
    )

    # Crear un detector sin iniciar
    # realmente MediaPipe.
    detector = HandDetector.__new__(
        HandDetector
    )

    detector.hands = DetectorSimulado()

    # Simular las herramientas de dibujo
    # para evitar dibujar puntos reales.
    detector.mp_hands = SimpleNamespace(
        HAND_CONNECTIONS=[]
    )

    llamadas = []

    def dibujo_simulado(*args):
        llamadas.append(args)

    detector.mp_drawing = SimpleNamespace(
        draw_landmarks=dibujo_simulado
    )

    # ACT:
    # Ejecutar el metodo real detectar().
    resultado = detector.detectar(imagen)

    # ASSERT:
    # Comprobar que se detecto una mano.
    assert len(resultado) == 1

    # Comprobar que la mano es derecha.
    assert resultado[0]["id"] == "Right"

    # Comprobar que existen 21 puntos.
    assert len(
        resultado[0]["landmarks"].landmark
    ) == 21

    # Comprobar que se llamo al dibujo.
    assert len(llamadas) == 1


def test_sustituir_deteccion_con_monkeypatch(
    monkeypatch,
):
    # ARRANGE:
    # Crear una respuesta falsa.
    mano_simulada = SimpleNamespace(
        landmark=[
            SimpleNamespace(x=0.5, y=0.5, z=0.0)
            for _ in range(21)
        ]
    )

    respuesta_simulada = [
        {
            "id": "Left",
            "landmarks": mano_simulada,
        }
    ]

    # Crear un detector sin inicializar
    # la camara ni MediaPipe.
    detector = HandDetector.__new__(
        HandDetector
    )

    # Reemplazar temporalmente detectar().
    monkeypatch.setattr(
        detector,
        "detectar",
        lambda imagen: respuesta_simulada,
    )

    imagen = np.zeros(
        (480, 640, 3),
        dtype=np.uint8,
    )

    # ACT:
    # Ejecutar la deteccion sustituida.
    resultado = detector.detectar(imagen)

    # ASSERT:
    # Comprobar la respuesta simulada.
    assert len(resultado) == 1
    assert resultado[0]["id"] == "Left"
    assert len(
        resultado[0]["landmarks"].landmark
    ) == 21
