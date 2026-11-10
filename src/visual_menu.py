
import cv2


class VisualMenu:
    def __init__(self):
        self.botones = []
        self.alto_menu = 180

        self.herramientas = [
            ("LIBRE", "tool_1"),
            ("LINEA", "tool_2"),
            ("RECT", "tool_3"),
            ("CIRCULO", "tool_4"),
            ("TRIANG", "tool_5"),
            ("BORRAR", "borrador"),
        ]

        self.colores = [
            ("ROJO", (0, 0, 255)),
            ("VERDE", (0, 255, 0)),
            ("AZUL", (255, 0, 0)),
            ("MORADO", (255, 0, 255)),
            ("AMARILLO", (0, 255, 255)),
            ("BLANCO", (255, 255, 255)),
        ]

        self.acciones = [
            ("LIMPIAR", "limpiar"),
            ("GUARDAR", "guardar"),
            ("NORMAL", "normal"),
            ("GRANDE", "grande"),
            ("COMPLETA", "completa"),
            ("GROSOR +", "mas"),
            ("GROSOR -", "menos"),
        ]

    def _agregar_boton(
        self,
        frame,
        texto,
        accion,
        x1,
        y1,
        x2,
        y2,
        fondo=(60, 65, 75),
        color_texto=(255, 255, 255),
    ):
        cv2.rectangle(frame, (x1, y1), (x2, y2), fondo, -1)
        cv2.rectangle(
            frame, (x1, y1), (x2, y2), (160, 160, 160), 1
        )

        escala = min(0.55, max(0.30, (x2 - x1) / 190))
        fuente = cv2.FONT_HERSHEY_SIMPLEX

        (tw, th), _ = cv2.getTextSize(
            texto, fuente, escala, 1
        )

        tx = x1 + max(0, (x2 - x1 - tw) // 2)
        ty = y1 + (y2 - y1 + th) // 2

        cv2.putText(
            frame,
            texto,
            (tx, ty),
            fuente,
            escala,
            color_texto,
            1,
            cv2.LINE_AA,
        )

        self.botones.append({
            "accion": accion,
            "rect": (x1, y1, x2, y2),
        })

    def _dibujar_fila(
        self, frame, elementos, y1, y2, colores=False
    ):
        ancho = frame.shape[1]
        margen = 12
        separacion = 8
        cantidad = len(elementos)

        espacio = ancho - 2 * margen
        ancho_boton = (
            espacio - separacion * (cantidad - 1)
        ) // cantidad

        for indice, elemento in enumerate(elementos):
            x1 = margen + indice * (
                ancho_boton + separacion
            )

            if indice == cantidad - 1:
                x2 = ancho - margen
            else:
                x2 = x1 + ancho_boton

            if colores:
                nombre, color = elemento

                color_texto = (
                    (0, 0, 0)
                    if nombre in ("VERDE", "AMARILLO", "BLANCO")
                    else (255, 255, 255)
                )

                self._agregar_boton(
                    frame,
                    nombre,
                    f"color_{nombre}",
                    x1,
                    y1,
                    x2,
                    y2,
                    fondo=color,
                    color_texto=color_texto,
                )
            else:
                nombre, accion = elemento

                self._agregar_boton(
                    frame,
                    nombre,
                    accion,
                    x1,
                    y1,
                    x2,
                    y2,
                )

    def dibujar(self, frame):
        self.botones.clear()

        alto, ancho = frame.shape[:2]

        cv2.rectangle(
            frame,
            (0, 0),
            (ancho, min(self.alto_menu, alto)),
            (25, 30, 40),
            -1,
        )

        self._dibujar_fila(
            frame, self.herramientas, 10, 58
        )

        self._dibujar_fila(
            frame, self.colores, 66, 114, colores=True
        )

        self._dibujar_fila(
            frame, self.acciones, 122, 170
        )

    def obtener_accion(self, punto):
        x, y = punto

        for boton in self.botones:
            x1, y1, x2, y2 = boton["rect"]

            if x1 <= x <= x2 and y1 <= y <= y2:
                return boton["accion"]

        return None

    def esta_en_menu(self, punto):
        return punto[1] < self.alto_menu
