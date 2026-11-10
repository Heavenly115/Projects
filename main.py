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
    5: "TRIANGULO"
}

FIGURAS = {
    2: Linea,
    3: Rectangulo,
    4: Circulo,
    5: Triangulo
}

COLORES_TECLAS = {
    ord("r"): "ROJO",
    ord("g"): "VERDE",
    ord("b"): "AZUL",
    ord("m"): "MORADO",
    ord("y"): "AMARILLO",
    ord("w"): "BLANCO"
}


def main():
    detector = HandDetector()
    reconocedor = GestureRecognizer()

    camara = cv2.VideoCapture(0)

    if not camara.isOpened():
        print("No se pudo abrir la cámara")
        detector.cerrar()
        return

    camara.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )
    camara.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    lienzo = None
    herramienta = 1

    # Una figura en progreso por cada mano.
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
                lienzo = CanvasController(
                    ancho,
                    alto
                )

            manos = detector.detectar(frame)

            manos_visibles = set()
            gestos = []

            for datos_mano in manos:
                mano_id = datos_mano["id"]
                mano = datos_mano["landmarks"]

                manos_visibles.add(mano_id)

                gesto = reconocedor.reconocer(mano)

                gestos.append(
                    f"{mano_id}: {gesto}"
                )

                indice = mano.landmark[8]

                x = max(
                    0,
                    min(
                        int(indice.x * ancho),
                        ancho - 1
                    )
                )

                y = max(
                    0,
                    min(
                        int(indice.y * alto),
                        alto - 1
                    )
                )

                punto = (x, y)

                if gesto == "DIBUJAR":

                    if (
                        herramienta == 1
                        or lienzo.modo_borrador
                    ):
                        lienzo.dibujar(
                            punto,
                            mano_id
                        )

                    else:
                        lienzo.pausar(mano_id)

                        if mano_id not in figuras_en_progreso:
                            figuras_en_progreso[mano_id] = {
                                "inicio": punto,
                                "fin": punto
                            }
                        else:
                            figuras_en_progreso[
                                mano_id
                            ]["fin"] = punto

                    # Puntero con el color de cada mano.
                    if lienzo.modo_borrador:
                        color_puntero = (0, 0, 0)
                    else:
                        color_puntero = (
                            lienzo.obtener_color(mano_id)
                        )

                    cv2.circle(
                        frame,
                        punto,
                        10,
                        color_puntero,
                        -1
                    )

                else:
                    lienzo.pausar(mano_id)

                    # Confirmar figura al dejar de dibujar.
                    if mano_id in figuras_en_progreso:
                        datos = figuras_en_progreso.pop(
                            mano_id
                        )

                        figura = FIGURAS[herramienta]()

                        lienzo.dibujar_figura(
                            figura,
                            datos["inicio"],
                            datos["fin"],
                            mano_id
                        )

            # Pausar manos que salieron de la cámara.
            for mano_id in list(
                lienzo.puntos_anteriores
            ):
                if mano_id not in manos_visibles:
                    lienzo.pausar(mano_id)

            # Cancelar figuras de manos desaparecidas.
            for mano_id in list(
                figuras_en_progreso
            ):
                if mano_id not in manos_visibles:
                    figuras_en_progreso.pop(
                        mano_id
                    )

            resultado = lienzo.combinar(frame)

            # Vista previa de figuras geométricas.
            if (
                herramienta != 1
                and not lienzo.modo_borrador
            ):
                for mano_id, datos in (
                    figuras_en_progreso.items()
                ):
                    figura = FIGURAS[herramienta](
                        color=lienzo.obtener_color(
                            mano_id
                        ),
                        grosor=lienzo.grosor
                    )

                    figura.dibujar(
                        resultado,
                        datos["inicio"],
                        datos["fin"]
                    )

            if lienzo.modo_borrador:
                modo = "BORRADOR"
            else:
                modo = HERRAMIENTAS[herramienta]

            # Información de las manos.
            cv2.putText(
                resultado,
                f"Manos detectadas: {len(manos)}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.putText(
                resultado,
                f"Herramienta: {modo}",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                resultado,
                (
                    "Mano seleccionada: "
                    f"{lienzo.mano_seleccionada}"
                ),
                (20, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                resultado,
                (
                    "Izquierda: "
                    f"{lienzo.colores_manos['Left']}"
                    " | Derecha: "
                    f"{lienzo.colores_manos['Right']}"
                ),
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                resultado,
                f"Grosor: {lienzo.grosor}",
                (20, 175),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            for indice_gesto, texto in enumerate(
                gestos
            ):
                cv2.putText(
                    resultado,
                    texto,
                    (
                        20,
                        210 + indice_gesto * 30
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2
                )

            # Instrucciones.
            cv2.putText(
                resultado,
                "Z Izquierda | X Derecha | R G B M Y W Colores",
                (20, alto - 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                2
            )

            cv2.putText(
                resultado,
                "1 Libre | 2 Linea | 3 Rect | 4 Circulo | 5 Triangulo",
                (20, alto - 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                2
            )

            cv2.putText(
                resultado,
                "E Borrador | +/- Grosor | C Limpiar | S Guardar | Q Salir",
                (20, alto - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "Dibujo con dos manos",
                resultado
            )

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == ord("q"):
                break

            elif tecla == ord("c"):
                lienzo.limpiar()
                figuras_en_progreso.clear()

            elif tecla == ord("s"):
                ruta = lienzo.guardar()
                print(
                    f"Dibujo guardado: {ruta}"
                )

            # Seleccionar mano izquierda.
            elif tecla == ord("z"):
                lienzo.seleccionar_mano("Left")
                print(
                    "Mano seleccionada: izquierda"
                )

            # Seleccionar mano derecha.
            elif tecla == ord("x"):
                lienzo.seleccionar_mano("Right")
                print(
                    "Mano seleccionada: derecha"
                )

            # Cambiar color de la mano seleccionada.
            elif tecla in COLORES_TECLAS:
                color = COLORES_TECLAS[tecla]

                lienzo.cambiar_color(color)
                figuras_en_progreso.clear()

                print(
                    f"Color de {lienzo.mano_seleccionada}: "
                    f"{color}"
                )

            elif tecla == ord("e"):
                lienzo.activar_borrador()
                figuras_en_progreso.clear()
                print("Borrador activado")

            elif tecla in (
                ord("+"),
                ord("=")
            ):
                lienzo.cambiar_grosor(
                    lienzo.grosor + 2
                )
                print(
                    "Grosor:",
                    lienzo.grosor
                )

            elif tecla == ord("-"):
                lienzo.cambiar_grosor(
                    lienzo.grosor - 2
                )
                print(
                    "Grosor:",
                    lienzo.grosor
                )

            elif ord("1") <= tecla <= ord("5"):
                herramienta = tecla - ord("0")

                lienzo.modo_borrador = False
                lienzo.pausar()
                figuras_en_progreso.clear()

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