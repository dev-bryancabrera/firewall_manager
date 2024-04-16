class FilterPacket:

    def __init__(
        self, id, nombre_filtro, tipo_filtro, filtro, contenido, fecha_creacion, user_id
    ) -> None:
        self.id = id
        self.nombre_filtro = nombre_filtro
        self.tipo_filtro = tipo_filtro
        self.filtro = filtro
        self.contenido = contenido
        self.fecha_creacion = fecha_creacion
        self.user_id = user_id
