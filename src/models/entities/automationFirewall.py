class Automation:
    def __init__(
        self,
        id,
        nombre,
        tipo,
        restriccion,
        restriccion_proxy,
        horario,
        estado,
        fecha_creacion,
        comunidad_id,
        user_id,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.tipo = tipo
        self.restriccion = restriccion
        self.restriccion_proxy = restriccion_proxy
        self.horario = horario
        self.estado = estado
        self.fecha_creacion = fecha_creacion
        self.comunidad_id = comunidad_id
        self.user_id = user_id
