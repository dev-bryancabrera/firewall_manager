class Config:
    SECRET_KEY = "B!1poNAt1T^%kvhUI*S^"


class DevelopmentConfig(Config):
    MYSQL_HOST = "192.168.0.115"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = ""
    MYSQL_DB = "sigcenter"
    MYSQL_PORT = 3306


config = {"development": DevelopmentConfig}
