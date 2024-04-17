from .connectDB import get_connection


class createTable:
    @classmethod
    def createTables(self):
        db = None
        try:
            db = get_connection()
            cursor = db.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS filtro_monitoreo (id INT AUTO_INCREMENT PRIMARY KEY, nombre_filtro VARCHAR(255), tipo_filtro VARCHAR(255), contenido TEXT, fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, user_id INT, FOREIGN KEY (user_id) REFERENCES user(id))"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS firewall_rules (id INT AUTO_INCREMENT PRIMARY KEY, nombre_regla VARCHAR(255), tipo_regla VARCHAR(255), fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, estado BOOLEAN, user_id INT, FOREIGN KEY (user_id) REFERENCES user(id))"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS firewall_rules_detail (id INT AUTO_INCREMENT PRIMARY KEY, regla VARCHAR(255), estado BOOLEAN, firewall_rule_id INT, FOREIGN KEY (firewall_rule_id) REFERENCES firewall_rules(id))"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS monitoreo_reporte (id INT AUTO_INCREMENT PRIMARY KEY, nombre_reporte VARCHAR(255), reporte LONGBLOB, fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, filtro_monitoreo TEXT, user_id INT, FOREIGN KEY (user_id) REFERENCES user(id))"
            )

            db.commit()
            cursor.close()
            db.close()
            return "Base de datos y tablas creadas correctamente"
        except Exception as ex:
            db.rollback()
            raise Exception(ex)
