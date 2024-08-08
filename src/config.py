class Config:
    SECRET_KEY = "B!1poNAt1T^%kvhUI*S^"


class DevelopmentConfig(Config):
    MYSQL_HOST = "192.168.0.165"
    MYSQL_USER = "tecnico"
    MYSQL_PASSWORD = "admin-tecnico"
    MYSQL_DB = "sigcenter"
    MYSQL_PORT = 3306


config = {"development": DevelopmentConfig}
