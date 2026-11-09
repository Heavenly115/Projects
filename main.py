
import cv2
from src.hand_detector import HandDetector

detector = HandDetector()
camara = cv2.VideoCapture(0)

while True:
    correcto, frame = camara.read()

    if not correcto:
        print("No se pudo acceder a la cámara")
        break

    frame = cv2.flip(frame, 1)
    mano = detector.detectar(frame)

    cv2.imshow("Detector de manos", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camara.release()
detector.cerrar()
cv2.destroyAllWindows()
