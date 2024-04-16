from flask import jsonify
from .entities.user import User
from .db.connectDB import get_connection


class modelUser:

    @classmethod
    def login(self, user):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, username, password_hash FROM user WHERE username='{}'".format(
                user.username
            )
            cursor.execute(sql)
            row = cursor.fetchone()
            db.close()
            if row != None:
                user = User(
                    row[0], row[1], User.check_password(row[2], user.password_hash)
                )
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, username FROM user WHERE id='{}'".format(id)
            cursor.execute(sql)
            row = cursor.fetchone()
            db.close()
            if row != None:
                logged_user = User(row[0], row[1], None)
                return logged_user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
