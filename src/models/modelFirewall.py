from .db.connectDB import get_connection


class modelFirewall:

    @classmethod
    def insertRule(self, firewall):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "INSERT INTO firewall_rules(nombre_regla, tipo_regla, fecha_creacion, estado, user_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(
                sql,
                (
                    firewall.nombre_regla,
                    firewall.tipo_regla,
                    firewall.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                    firewall.estado,
                    firewall.user_id,
                ),
            )
            db.commit()
            firewall.id = cursor.lastrowid  # Asigna el lastrowid al objeto firewall
            db.close()
            return firewall
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def updateRule(self, estado, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "UPDATE firewall_rules SET estado = %s WHERE id = %s"
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
    def deleteRule(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "DELETE FROM firewall_rules WHERE id='{}'".format(id)
            cursor.execute(sql)
            db.commit()
            db.close()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def getRulesDeactivate(self):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT nombre_regla, estado FROM firewall_rules WHERE deactivate_rule IS NOT NULL"
            cursor.execute(sql)
            db.close()
            return cursor.fetchall()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getRules(self):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT * FROM firewall_rules"
            cursor.execute(sql)
            db.close()
            return cursor.fetchall()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getRuleByName(self, regla_nombre):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, user_id, nombre_regla, tipo_regla, fecha_creacion, estado FROM firewall_rules WHERE nombre_regla='{}'".format(
                regla_nombre
            )
            cursor.execute(sql)
            db.close()
            return cursor.fetchone()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getRuleById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, user_id, nombre_regla, tipo_regla, fecha_creacion, estado FROM firewall_rules WHERE id='{}'".format(
                id
            )
            cursor.execute(sql)
            db.close()
            return cursor.fetchone()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getRulesContent(self):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT * FROM firewall_rules WHERE tipo_regla='contenido'"
            cursor.execute(sql)
            db.close()
            return cursor.fetchall()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getRulesDefault(self):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT * FROM firewall_rules WHERE tipo_regla='predefinida'"
            cursor.execute(sql)
            db.close()
            return cursor.fetchall()
        except Exception as ex:
            raise Exception(ex)
