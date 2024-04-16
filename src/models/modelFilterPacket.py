from .db.connectDB import get_connection


class modelFilterPacket:

    @classmethod
    def insertFilter(self, filtro):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "INSERT INTO filtro_monitoreo(nombre_filtro, tipo_filtro, filtro, contenido, fecha_creacion, user_id) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(
                sql,
                (
                    filtro.nombre_filtro,
                    filtro.tipo_filtro,
                    filtro.filtro,
                    filtro.contenido,
                    filtro.fecha_creacion.strftime("%Y-%m-%d"),
                    filtro.user_id,
                ),
            )
            db.commit()
            db.close()
            return cursor.lastrowid
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def deleteFilter(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "DELETE FROM filtro_monitoreo WHERE id='{}'".format(id)
            cursor.execute(sql)
            db.commit()
            db.close()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def getFilters(self):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT * FROM filtro_monitoreo"
            cursor.execute(sql)
            db.close()
            return cursor.fetchall()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def getFiltersById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT * FROM filtro_monitoreo WHERE id='{}'".format(id)
            cursor.execute(sql)
            db.close()
            return cursor.fetchone()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)
