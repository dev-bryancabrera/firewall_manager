class Community:
    def __init__(
        self, id, nombre, tipo, rango, fecha_creacion, estado, user_id
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.tipo = tipo
        self.rango = rango
        self.fecha_creacion = fecha_creacion
        self.estado = estado
        self.user_id = user_id
