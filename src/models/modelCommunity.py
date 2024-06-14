from .db.connectDB import get_connection


class modelCommunity:
    @classmethod
    def insertCommunity(self, community):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "INSERT INTO comunidades (nombre, tipo, rango, fecha_creacion, estado, user_id) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(
                sql,
                (
                    community.nombre,
                    community.tipo,
                    community.rango,
                    community.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                    community.estado,
                    community.user_id,
                ),
            )
            db.commit()
            db.close()
            return community
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def updateCommunity(self, estado, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "UPDATE comunidades SET estado = %s WHERE id = %s"
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
    def deleteCommunity(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "DELETE FROM comunidades WHERE id='{}'".format(id)
            cursor.execute(sql)
            db.commit()
            db.close()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def getCommunity(self):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT * FROM comunidades"
            cursor.execute(sql)
            db.close()
            return cursor.fetchall()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getCommunityById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, nombre, tipo, rango, fecha_creacion, estado, user_id FROM comunidades WHERE id='{}'".format(
                id
            )
            cursor.execute(sql)
            db.close()
            return cursor.fetchone()
        except Exception as ex:
            raise Exception(ex)
