class Firewall:
    def __init__(
        self,
        id,
        nombre_regla,
        tipo_regla,
        fecha_creacion,
        estado,
        # automation_status,
        user_id,
    ) -> None:
        self.id = id
        self.nombre_regla = nombre_regla
        self.tipo_regla = tipo_regla
        self.fecha_creacion = fecha_creacion
        self.estado = estado
        # self.automation_status = automation_status
        self.user_id = user_id
