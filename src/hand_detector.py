import cv2
import mediapipe as mp


class HandDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def detectar(self, frame):
        imagen_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagen_rgb.flags.writeable = False

        resultados = self.hands.process(imagen_rgb)

        manos = []

        if resultados.multi_hand_landmarks:
            for mano in resultados.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    mano,
                    self.mp_hands.HAND_CONNECTIONS
                )
                manos.append(mano)

        return manos

    def cerrar(self):
        self.hands.close()