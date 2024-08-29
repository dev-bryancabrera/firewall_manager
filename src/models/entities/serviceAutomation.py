class servAutomation:
    def __init__(
        self,
        id,
        nombre,
        servicio,
        restriccion,
        tipo_alerta,
        datos_restriccion,
        fecha_creacion,
        estado,
        comunidad_id,
        user_id,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.servicio = servicio
        self.restriccion = restriccion
        self.tipo_alerta = tipo_alerta
        self.datos_restriccion = datos_restriccion
        self.fecha_creacion = fecha_creacion
        self.estado = estado
        self.comunidad_id = comunidad_id
        self.user_id = user_id
