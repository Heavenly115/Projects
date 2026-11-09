class GestureRecognizer:
    """Reconoce gestos básicos a partir de los puntos de una mano."""

    def dedos_levantados(self, mano):
        """
        Devuelve el estado de cuatro dedos:
        [índice, medio, anular, meñique].

        True significa levantado.
        False significa doblado.
        """
        if mano is None:
            return [False, False, False, False]

        puntos = mano.landmark

        pares = [
            (8, 6),    # Índice
            (12, 10),  # Medio
            (16, 14),  # Anular
            (20, 18),  # Meñique
        ]

        return [
            puntos[yema].y < puntos[articulacion].y
            for yema, articulacion in pares
        ]

    def reconocer(self, mano):
        """Identifica el gesto realizado por la mano."""
        if mano is None:
            return "SIN_MANO"

        dedos = self.dedos_levantados(mano)

        if dedos == [True, False, False, False]:
            return "DIBUJAR"

        if dedos == [True, True, False, False]:
            return "PAUSA"

        if dedos == [False, False, False, False]:
            return "PUNO"

        if dedos == [True, True, True, True]:
            return "MANO_ABIERTA"

        return "DESCONOCIDO"