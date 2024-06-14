from .db.connectDB import get_connection


class modelAutomation:
    @classmethod
    def insertAutomation(self, automation):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "INSERT INTO automatizacion_firewall (nombre, tipo, restriccion, horario, estado, fecha_creacion, comunidad_id, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(
                sql,
                (
                    automation.nombre,
                    automation.tipo,
                    automation.restriccion,
                    automation.horario,
                    automation.estado,
                    automation.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
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
    def updateAutomation(self, estado, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "UPDATE automatizacion_firewall SET estado = %s WHERE id = %s"
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
    def deleteAutomation(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "DELETE FROM automatizacion_firewall WHERE id='{}'".format(id)
            cursor.execute(sql)
            db.commit()
            db.close()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def getAutomation(self):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT * FROM automatizacion_firewall"
            cursor.execute(sql)
            db.close()
            return cursor.fetchall()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getAutomationById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT nombre, tipo, horario, restriccion, estado, fecha_creacion, comunidad_id, user_id FROM automatizacion_firewall WHERE id='{}'".format(
                id
            )
            cursor.execute(sql)
            db.close()
            return cursor.fetchone()
        except Exception as ex:
            raise Exception(ex)
