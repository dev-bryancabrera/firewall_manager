from .db.connectDB import get_connection


class modelServiceAutomation:
    @classmethod
    def insertServAutomation(self, automation):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = """
            INSERT INTO service_restriction 
            (nombre, servicio, restriccion, tipo_alerta, datos_restriccion, fecha_creacion, estado, comunidad_id, user_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                sql,
                (
                    automation.nombre,
                    automation.servicio,
                    automation.restriccion,
                    automation.tipo_alerta,
                    automation.datos_restriccion,
                    automation.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                    automation.estado,
                    automation.comunidad_id,
                    automation.user_id,
                ),
            )
            db.commit()
            db.close()
            return automation
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def updateServAutomation(self, estado, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "UPDATE service_restriction SET estado = %s WHERE id = %s"
            cursor.execute(
                sql,
                (
                    estado,
                    id,
                ),
            )
            db.commit()
            db.close()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def deleteServAutomation(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "DELETE FROM service_restriction WHERE id='{}'".format(id)
            cursor.execute(sql)
            db.commit()
            db.close()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def getServAutomation(self):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, nombre, servicio, restriccion, tipo_alerta, datos_restriccion, fecha_creacion, estado, comunidad_id, user_id FROM service_restriction"
            cursor.execute(sql)
            db.close()
            return cursor.fetchall()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getServAutomationById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, nombre, servicio, restriccion, tipo_alerta, datos_restriccion, fecha_creacion, estado, comunidad_id, user_id FROM service_restriction WHERE id='{}'".format(
                id
            )
            cursor.execute(sql)
            db.close()
            return cursor.fetchone()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getCommunityById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, nombre, servicio, restriccion, tipo_alerta, datos_restriccion, fecha_creacion, estado, comunidad_id, user_id FROM service_restriction WHERE comunidad_id='{}'".format(
                id
            )
            cursor.execute(sql)
            db.close()
            return cursor.fetchone()
        except Exception as ex:
            raise Exception(ex)
