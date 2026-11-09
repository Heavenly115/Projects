import cv2

from src.hand_detector import HandDetector
from src.gesture_recognizer import GestureRecognizer
from src.canvas_controller import CanvasController


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

            # Por ahora dibujamos con una mano.
            # El detector puede encontrar hasta dos.
            if manos:
                mano = manos[0]
                gesto = reconocedor.reconocer(mano)

                if gesto == "DIBUJAR":
                    # Punto 8 = yema del dedo índice
                    indice = mano.landmark[8]

                    x = int(indice.x * ancho)
                    y = int(indice.y * alto)

                    x = max(0, min(x, ancho - 1))
                    y = max(0, min(y, alto - 1))

                    lienzo.dibujar((x, y))

                    cv2.circle(
                        frame,
                        (x, y),
                        10,
                        (0, 255, 0),
                        -1
                    )
                else:
                    lienzo.pausar()

            else:
                gesto = "SIN_MANO"
                lienzo.pausar()

            resultado = lienzo.combinar(frame)

            cv2.putText(
                resultado,
                f"Gesto: {gesto}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.putText(
                resultado,
                "Indice: dibujar | Dos dedos: pausa",
                (20, alto - 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                resultado,
                "C: borrar | S: guardar | Q: salir",
                (20, alto - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.imshow("Dibujo con gestos", resultado)

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == ord("q"):
                break

            elif tecla == ord("c"):
                lienzo.limpiar()
                print("Lienzo borrado")

            elif tecla == ord("s"):
                ruta = lienzo.guardar()
                print(f"Dibujo guardado en: {ruta}")

    finally:
        camara.release()
        detector.cerrar()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()