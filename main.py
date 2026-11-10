import cv2

from src.hand_detector import HandDetector
from src.gesture_recognizer import GestureRecognizer
from src.canvas_controller import CanvasController
from src.drawing import Linea, Rectangulo, Circulo, Triangulo


HERRAMIENTAS = {
    1: "LIBRE",
    2: "LINEA",
    3: "RECTANGULO",
    4: "CIRCULO",
    5: "TRIANGULO",
}

FIGURAS = {
    2: Linea,
    3: Rectangulo,
    4: Circulo,
    5: Triangulo,
}


def main():
    detector = HandDetector()
    reconocedor = GestureRecognizer()
    camara = cv2.VideoCapture(0)

    if not camara.isOpened():
        print("No se pudo abrir la cámara")
        detector.cerrar()
        return

    camara.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    lienzo = None
    herramienta = 1

    # Cada mano tendrá su propia figura en progreso
    figuras_en_progreso = {}

    try:
        while True:
            correcto, frame = camara.read()

            if not correcto:
                print("No se pudo leer la cámara")
                break

            frame = cv2.flip(frame, 1)
            alto, ancho = frame.shape[:2]

            if lienzo is None:
                lienzo = CanvasController(ancho, alto)

            manos = detector.detectar(frame)
            manos_visibles = set()
            gestos = []

            for datos_mano in manos:
                mano_id = datos_mano["id"]
                mano = datos_mano["landmarks"]

                manos_visibles.add(mano_id)

                gesto = reconocedor.reconocer(mano)
                gestos.append(f"{mano_id}: {gesto}")

                indice = mano.landmark[8]

                x = max(
                    0,
                    min(int(indice.x * ancho), ancho - 1)
                )
                y = max(
                    0,
                    min(int(indice.y * alto), alto - 1)
                )

                punto = (x, y)

                if gesto == "DIBUJAR":
                    if herramienta == 1:
                        lienzo.dibujar(punto, mano_id)
                    else:
                        lienzo.pausar(mano_id)

                        if mano_id not in figuras_en_progreso:
                            figuras_en_progreso[mano_id] = {
                                "inicio": punto,
                                "fin": punto
                            }
                        else:
                            figuras_en_progreso[mano_id]["fin"] = punto

                    color = lienzo.colores.get(
                        mano_id, (255, 255, 255)
                    )

                    cv2.circle(
                        frame, punto, 10, color, -1
                    )

                else:
                    lienzo.pausar(mano_id)

                    # Confirmar figura cuando cambia el gesto
                    if mano_id in figuras_en_progreso:
                        datos = figuras_en_progreso.pop(mano_id)

                        figura = FIGURAS[herramienta](
                            color=lienzo.colores.get(
                                mano_id, (255, 255, 255)
                            )
                        )

                        lienzo.dibujar_figura(
                            figura,
                            datos["inicio"],
                            datos["fin"]
                        )

            # Pausar las manos que desaparecieron
            for mano_id in list(lienzo.puntos_anteriores):
                if mano_id not in manos_visibles:
                    lienzo.pausar(mano_id)

            # Cancelar figuras de manos que desaparecieron
            for mano_id in list(figuras_en_progreso):
                if mano_id not in manos_visibles:
                    figuras_en_progreso.pop(mano_id)

            resultado = lienzo.combinar(frame)

            # Vista previa de las figuras de ambas manos
            if herramienta != 1:
                for mano_id, datos in figuras_en_progreso.items():
                    figura = FIGURAS[herramienta](
                        color=lienzo.colores.get(
                            mano_id, (255, 255, 255)
                        )
                    )

                    figura.dibujar(
                        resultado,
                        datos["inicio"],
                        datos["fin"]
                    )

            cv2.putText(
                resultado,
                f"Manos detectadas: {len(manos)}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.putText(
                resultado,
                f"Herramienta: {HERRAMIENTAS[herramienta]}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            for indice, texto in enumerate(gestos):
                cv2.putText(
                    resultado,
                    texto,
                    (20, 120 + indice * 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

            cv2.putText(
                resultado,
                "1 Libre | 2 Linea | 3 Rect | 4 Circulo | 5 Triangulo",
                (20, alto - 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2
            )

            cv2.putText(
                resultado,
                "C Borrar | S Guardar | Q Salir",
                (20, alto - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.imshow("Dibujo con dos manos", resultado)

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == ord("q"):
                break

            elif tecla == ord("c"):
                lienzo.limpiar()
                figuras_en_progreso.clear()

            elif tecla == ord("s"):
                ruta = lienzo.guardar()
                print(f"Dibujo guardado: {ruta}")

            elif ord("1") <= tecla <= ord("5"):
                herramienta = tecla - ord("0")
                figuras_en_progreso.clear()
                lienzo.pausar()

                print(
                    "Herramienta seleccionada:",
                    HERRAMIENTAS[herramienta]
                )

    finally:
        camara.release()
        detector.cerrar()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()