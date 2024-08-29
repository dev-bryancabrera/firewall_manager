from .db.connectDB import get_connection


class modelNotification:
    @classmethod
    def insertNotification(self, notification):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = (
                "INSERT INTO notificaciones (mensaje, leido, fecha) VALUES (%s, %s, %s)"
            )
            cursor.execute(
                sql,
                (
                    notification.mensaje,
                    notification.leido,
                    notification.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            db.commit()
            db.close()
            return notification
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def updateNotification(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "UPDATE notificaciones SET leido = %s WHERE id = %s"
            cursor.execute(
                sql,
                (
                    1,
                    id,
                ),
            )
            db.commit()
            db.close()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def deleteNotification(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "DELETE FROM notificaciones WHERE id='{}'".format(id)
            cursor.execute(sql)
            db.commit()
            db.close()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def getNotifications(self):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, mensaje, leido, fecha FROM notificaciones"
            cursor.execute(sql)
            db.close()
            return cursor.fetchall()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getNotificationById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, mensaje, leido, fecha FROM notificaciones WHERE id='{}'".format(
                id
            )
            cursor.execute(sql)
            db.close()
            return cursor.fetchone()
        except Exception as ex:
            raise Exception(ex)
