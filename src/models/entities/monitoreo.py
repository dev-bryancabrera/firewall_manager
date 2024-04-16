class Monitoreo:

    def __init__(
        self, id, nombre_reporte, reporte, fecha_creacion, filtro_monitoreo, user_id
    ) -> None:
        self.id = id
        self.nombre_reporte = nombre_reporte
        self.reporte = reporte
        self.fecha_creacion = fecha_creacion
        self.filtro_monitoreo = filtro_monitoreo
        self.user_id = user_id
