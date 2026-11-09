
import cv2
import mediapipe as mp


class HandDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def detectar(self, frame):
        imagen_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = self.hands.process(imagen_rgb)

        if resultados.multi_hand_landmarks:
            mano = resultados.multi_hand_landmarks[0]

            self.mp_drawing.draw_landmarks(
                frame,
                mano,
                self.mp_hands.HAND_CONNECTIONS
            )

            return mano

        return None

    def cerrar(self):
        self.hands.close()
