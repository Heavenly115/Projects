
import cv2
import numpy as np

from src.hand_detector import HandDetector
from src.gesture_recognizer import GestureRecognizer
from src.canvas_controller import CanvasController
from src.drawing import Linea, Rectangulo, Circulo, Triangulo
from src.visual_menu import VisualMenu


NOMBRE_VENTANA = "Dibujo con dos manos"

ANCHO_PANTALLA = 1920
ALTO_PANTALLA = 1080

ALTO_MENU = 180
ALTO_ESTADO = 100

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

COLORES_TECLAS = {
    ord("r"): "ROJO",
    ord("g"): "VERDE",
    ord("b"): "AZUL",
    ord("m"): "MORADO",
    ord("y"): "AMARILLO",
    ord("w"): "BLANCO",
}


def cambiar_tamano(modo):
    if modo == "completa":
        cv2.setWindowProperty(
            NOMBRE_VENTANA,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN,
        )
        return

    cv2.setWindowProperty(
        NOMBRE_VENTANA,
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_NORMAL,
    )

    if modo == "normal":
        cv2.resizeWindow(
            NOMBRE_VENTANA, 960, 540
        )

    elif modo == "grande":
        cv2.resizeWindow(
            NOMBRE_VENTANA, 1600, 900
        )


def calcular_area_camara(ancho_origen, alto_origen):
    """
    Calcula el tamaño de la camara dentro de
    la zona disponible, sin deformar la imagen.
    """
    ancho_disponible = ANCHO_PANTALLA
    alto_disponible = (
        ALTO_PANTALLA - ALTO_MENU - ALTO_ESTADO
    )

    escala = min(
        ancho_disponible / ancho_origen,
        alto_disponible / alto_origen,
    )

    ancho_final = max(
        1, int(ancho_origen * escala)
    )
    alto_final = max(
        1, int(alto_origen * escala)
    )

    x = (ANCHO_PANTALLA - ancho_final) // 2
    y = ALTO_MENU + (
        alto_disponible - alto_final
    ) // 2

    return x, y, ancho_final, alto_final


def main():
    detector = HandDetector()
    reconocedor = GestureRecognizer()
    menu = VisualMenu()

    camara = cv2.VideoCapture(0)

    if not camara.isOpened():
        print("No se pudo abrir la camara")
        detector.cerrar()
        return

    camara.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    cv2.namedWindow(
        NOMBRE_VENTANA,
        cv2.WINDOW_NORMAL,
    )

    cv2.resizeWindow(
        NOMBRE_VENTANA,
        ANCHO_PANTALLA,
        ALTO_PANTALLA,
    )

    cambiar_tamano("completa")

    lienzo = None
    herramienta = 1

    figuras_en_progreso = {}
    pinzas_anteriores = {}

    def procesar_accion(accion, mano_id=None):
        nonlocal herramienta

        if accion is None:
            return

        if accion.startswith("tool_"):
            herramienta = int(
                accion.split("_")[1]
            )

            lienzo.desactivar_borrador()
            lienzo.pausar()
            figuras_en_progreso.clear()

            print(
                "Herramienta:",
                HERRAMIENTAS[herramienta],
            )

        elif accion.startswith("color_"):
            color = accion.replace("color_", "")

            if mano_id is None:
                mano_id = lienzo.mano_seleccionada

            lienzo.cambiar_color(
                color, mano_id
            )

            figuras_en_progreso.clear()

            print(
                f"Color de {mano_id}: {color}"
            )

        elif accion == "borrador":
            lienzo.activar_borrador()
            figuras_en_progreso.clear()
            print("Borrador activado")

        elif accion == "limpiar":
            lienzo.limpiar()
            figuras_en_progreso.clear()
            print("Lienzo limpiado")

        elif accion == "guardar":
            ruta = lienzo.guardar()
            print(
                f"Dibujo guardado: {ruta}"
            )

        elif accion in (
            "normal", "grande", "completa"
        ):
            cambiar_tamano(accion)

        elif accion == "mas":
            lienzo.cambiar_grosor(
                lienzo.grosor + 2
            )

        elif accion == "menos":
            lienzo.cambiar_grosor(
                lienzo.grosor - 2
            )

    try:
        while True:
            correcto, frame = camara.read()

            if not correcto:
                print(
                    "No se pudo leer la camara"
                )
                break

            frame = cv2.flip(frame, 1)

            alto, ancho = frame.shape[:2]

            if lienzo is None:
                lienzo = CanvasController(
                    ancho, alto
                )

            manos = detector.detectar(frame)
            manos_visibles = set()

            # Creamos SIEMPRE una pantalla
            # completa de 1920 x 1080.
            pantalla = np.zeros(
                (
                    ALTO_PANTALLA,
                    ANCHO_PANTALLA,
                    3
                ),
                dtype=np.uint8,
            )

            # Menu superior en todo el ancho.
            menu.dibujar(pantalla)

            # Calculamos donde se mostrara
            # la camara ampliada.
            x_camara, y_camara, ancho_camara, alto_camara = (
                calcular_area_camara(
                    ancho, alto
                )
            )

            for datos_mano in manos:
                mano_id = datos_mano["id"]
                mano = datos_mano["landmarks"]

                manos_visibles.add(mano_id)

                gesto = reconocedor.reconocer(
                    mano
                )

                indice = mano.landmark[8]

                x = max(
                    0,
                    min(
                        int(indice.x * ancho),
                        ancho - 1,
                    ),
                )

                y = max(
                    0,
                    min(
                        int(indice.y * alto),
                        alto - 1,
                    ),
                )

                punto = (x, y)

                # Convertimos la posicion
                # de la mano a coordenadas
                # de la pantalla 1920x1080.
                x_pantalla = (
                    x_camara
                    + int(
                        x * ancho_camara / ancho
                    )
                )

                y_pantalla = (
                    y_camara
                    + int(
                        y * alto_camara / alto
                    )
                )

                pinza = reconocedor.es_pinza(
                    mano
                )

                pinza_anterior = (
                    pinzas_anteriores.get(
                        mano_id, False
                    )
                )

                # El menu se selecciona usando
                # una zona virtual superior
                # de la imagen de camara.
                #
                # Convertimos la posicion
                # horizontal al menu real.
                x_menu = int(
                    x * ANCHO_PANTALLA / ancho
                )

                y_menu = int(
                    y * ALTO_MENU / max(
                        1, int(alto * 0.25)
                    )
                )

                zona_menu = (
                    y < int(alto * 0.25)
                )

                if (
                    pinza
                    and not pinza_anterior
                    and zona_menu
                ):
                    accion = menu.obtener_accion(
                        (x_menu, y_menu)
                    )

                    if accion is not None:
                        procesar_accion(
                            accion, mano_id
                        )

                pinzas_anteriores[
                    mano_id
                ] = pinza

                # Evitar dibujar mientras
                # se usa el menu o la pinza.
                if zona_menu or pinza:
                    lienzo.pausar(mano_id)
                    figuras_en_progreso.pop(
                        mano_id, None
                    )
                    continue

                if gesto == "DIBUJAR":
                    if (
                        herramienta == 1
                        or lienzo.modo_borrador
                    ):
                        lienzo.dibujar(
                            punto, mano_id
                        )

                    else:
                        lienzo.pausar(mano_id)

                        if (
                            mano_id
                            not in figuras_en_progreso
                        ):
                            figuras_en_progreso[
                                mano_id
                            ] = {
                                "inicio": punto,
                                "fin": punto,
                            }

                        else:
                            figuras_en_progreso[
                                mano_id
                            ]["fin"] = punto

                else:
                    lienzo.pausar(mano_id)

                    if (
                        mano_id
                        in figuras_en_progreso
                    ):
                        datos = (
                            figuras_en_progreso.pop(
                                mano_id
                            )
                        )

                        figura = FIGURAS[
                            herramienta
                        ]()

                        lienzo.dibujar_figura(
                            figura,
                            datos["inicio"],
                            datos["fin"],
                            mano_id,
                        )

            # Limpiar manos ausentes.
            for mano_id in list(
                lienzo.puntos_anteriores
            ):
                if mano_id not in manos_visibles:
                    lienzo.pausar(mano_id)

            for mano_id in list(
                figuras_en_progreso
            ):
                if mano_id not in manos_visibles:
                    figuras_en_progreso.pop(
                        mano_id
                    )

            for mano_id in list(
                pinzas_anteriores
            ):
                if mano_id not in manos_visibles:
                    pinzas_anteriores.pop(
                        mano_id
                    )

            resultado = lienzo.combinar(
                frame
            )

            # Vista previa de figuras.
            if (
                herramienta != 1
                and not lienzo.modo_borrador
            ):
                for mano_id, datos in (
                    figuras_en_progreso.items()
                ):
                    figura = FIGURAS[
                        herramienta
                    ](
                        color=lienzo.obtener_color(
                            mano_id
                        ),
                        grosor=lienzo.grosor,
                    )

                    figura.dibujar(
                        resultado,
                        datos["inicio"],
                        datos["fin"],
                    )

            # Ampliar la camara para
            # aprovechar el espacio.
            camara_ampliada = cv2.resize(
                resultado,
                (
                    ancho_camara,
                    alto_camara
                ),
                interpolation=cv2.INTER_LINEAR,
            )

            pantalla[
                y_camara:y_camara + alto_camara,
                x_camara:x_camara + ancho_camara,
            ] = camara_ampliada

            # Barra inferior.
            inicio_estado = (
                ALTO_PANTALLA - ALTO_ESTADO
            )

            cv2.rectangle(
                pantalla,
                (0, inicio_estado),
                (
                    ANCHO_PANTALLA,
                    ALTO_PANTALLA
                ),
                (30, 35, 45),
                -1,
            )

            modo = (
                "BORRADOR"
                if lienzo.modo_borrador
                else HERRAMIENTAS[
                    herramienta
                ]
            )

            cv2.putText(
                pantalla,
                (
                    f"Herramienta: {modo}"
                    f" | Grosor: {lienzo.grosor}"
                ),
                (30, inicio_estado + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )

            cv2.putText(
                pantalla,
                (
                    f"Izquierda: "
                    f"{lienzo.colores_manos['Left']}"
                    f" | Derecha: "
                    f"{lienzo.colores_manos['Right']}"
                ),
                (30, inicio_estado + 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                pantalla,
                (
                    "F completa | N normal | "
                    "V grande | ESC salir | "
                    "Z/X mano | R G B M Y W colores"
                ),
                (30, inicio_estado + 87),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
            )

            cv2.imshow(
                NOMBRE_VENTANA,
                pantalla,
            )

            tecla = cv2.waitKey(1) & 0xFF

            if tecla in (ord("q"), 27):
                break

            elif tecla == ord("z"):
                lienzo.seleccionar_mano(
                    "Left"
                )

            elif tecla == ord("x"):
                lienzo.seleccionar_mano(
                    "Right"
                )

            elif tecla in COLORES_TECLAS:
                procesar_accion(
                    "color_"
                    + COLORES_TECLAS[
                        tecla
                    ]
                )

            elif tecla == ord("e"):
                procesar_accion(
                    "borrador"
                )

            elif tecla == ord("c"):
                procesar_accion(
                    "limpiar"
                )

            elif tecla == ord("s"):
                procesar_accion(
                    "guardar"
                )

            elif tecla == ord("f"):
                procesar_accion(
                    "completa"
                )

            elif tecla == ord("n"):
                procesar_accion(
                    "normal"
                )

            elif tecla == ord("v"):
                procesar_accion(
                    "grande"
                )

            elif tecla in (
                ord("+"), ord("=")
            ):
                procesar_accion(
                    "mas"
                )

            elif tecla == ord("-"):
                procesar_accion(
                    "menos"
                )

            elif (
                ord("1")
                <= tecla
                <= ord("5")
            ):
                numero = (
                    tecla - ord("0")
                )

                procesar_accion(
                    f"tool_{numero}"
                )

    finally:
        camara.release()
        detector.cerrar()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
