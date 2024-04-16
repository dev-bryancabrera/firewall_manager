from .db.connectDB import get_connection


class modelFirewallDetail:

    @classmethod
    def insertRuleDetail(self, firewallDetail):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "INSERT INTO firewall_rules_detail(rule_id, regla, estado) VALUES (%s, %s, %s)"
            cursor.execute(
                sql,
                (firewallDetail.rule_id, firewallDetail.regla, firewallDetail.estado),
            )
            db.commit()
            db.close()
            return cursor.lastrowid
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def updateDetail(self, estado, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "UPDATE firewall_rules_detail SET estado = %s WHERE id = %s"
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
    def deleteRuleDetail(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "DELETE FROM firewall_rules_detail WHERE rule_id='{}'".format(id)
            cursor.execute(sql)
            db.commit()
            db.close()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def deleteDetailById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "DELETE FROM firewall_rules_detail WHERE id='{}'".format(id)
            cursor.execute(sql)
            db.commit()
            db.close()
        except Exception as ex:
            db.rollback()
            raise Exception(ex)

    @classmethod
    def getRulesDetails(self):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT * FROM firewall_rules_detail"
            cursor.execute(sql)
            db.close()
            return cursor.fetchall()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getRulesDetailsById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, regla, estado FROM firewall_rules_detail WHERE rule_id = %s"
            cursor.execute(sql, (id,))
            details = cursor.fetchall()
            db.close()
            return details
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getRuleDetailById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = (
                "SELECT id, regla FROM firewall_rules_detail WHERE rule_id='{}'".format(
                    id
                )
            )
            cursor.execute(sql)
            db.close()
            return cursor.fetchone()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def getDetailById(self, id):
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = "SELECT id, regla, estado FROM firewall_rules_detail WHERE id='{}'".format(id)
            cursor.execute(sql)
            db.close()
            return cursor.fetchone()
        except Exception as ex:
            raise Exception(ex)
