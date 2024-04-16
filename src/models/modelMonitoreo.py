from .db.connectDB import get_connection


class modelPaquetes:

    @classmethod
    def insertPacket(self, monitoreo):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "INSERT INTO monitoreo_reporte(nombre_reporte, reporte, fecha_creacion, filtro_monitoreo, user_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(
                sql,
                (
                    monitoreo.nombre_reporte,
                    monitoreo.reporte,
                    monitoreo.fecha_creacion.strftime("%Y-%m-%d"),
                    monitoreo.filtro_monitoreo,
                    monitoreo.user_id,
                ),
            )
            db.commit()
            db.close()
            return cursor.lastrowid
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def deletePacket(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "DELETE FROM monitoreo_reporte WHERE id='{}'".format(id)
            cursor.execute(sql)
            db.commit()
            db.close()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def getPackets(self):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, nombre_reporte, fecha_creacion, filtro_monitoreo FROM monitoreo_reporte"
            cursor.execute(sql)
            db.close()
            return cursor.fetchall()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getPacketById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT reporte FROM monitoreo_reporte WHERE id='{}'".format(id)
            cursor.execute(sql)
            db.close()
            return cursor.fetchone()
        except Exception as ex:
            raise Exception(ex)
