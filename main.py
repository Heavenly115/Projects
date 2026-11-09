import cv2

from src.hand_detector import HandDetector
from src.gesture_recognizer import GestureRecognizer


def main():
    detector = HandDetector()
    reconocedor = GestureRecognizer()
    camara = cv2.VideoCapture(0)

    if not camara.isOpened():
        print("No se pudo abrir la cámara")
        detector.cerrar()
        return

    try:
        while True:
            correcto, frame = camara.read()

            if not correcto:
                print("No se pudo leer la cámara")
                break

            frame = cv2.flip(frame, 1)

            mano = detector.detectar(frame)
            gesto = reconocedor.reconocer(mano)

            cv2.putText(
                frame,
                f"Gesto: {gesto}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow("Reconocimiento de gestos", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camara.release()
        detector.cerrar()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()