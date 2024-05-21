class Config:
    SECRET_KEY = "B!1poNAt1T^%kvhUI*S^"


class DevelopmentConfig(Config):
    MYSQL_HOST = "192.168.100.43"
    MYSQL_USER = "tecnico"
    MYSQL_PASSWORD = "IntelHome123"
    MYSQL_DB = "SIG_CENTER"
    MYSQL_PORT = 3306


config = {"development": DevelopmentConfig}
