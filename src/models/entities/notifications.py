class Notification:
    def __init__(
        self,
        id,
        mensaje,
        leido,
        fecha,
    ) -> None:
        self.id = id
        self.mensaje = mensaje
        self.leido = leido
        self.fecha = fecha
