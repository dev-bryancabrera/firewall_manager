class Config:
    SECRET_KEY = "B!1poNAt1T^%kvhUI*S^"
    # MAIL_RECEIVER = "bsebastian.cabrera@gmail.com"

class DevelopmentConfig(Config):
    MYSQL_HOST = "192.168.0.165"
    MYSQL_USER = "tecnico"
    MYSQL_PASSWORD = "admin-tecnico"
    MYSQL_DB = "sigcenter"
    MYSQL_PORT = 3306

    # Configuración de Flask-Mail
    # MAIL_SERVER = "smtp.gmail.com"
    # MAIL_PORT = 587
    # MAIL_USERNAME = "bcsebastian99@gmail.com"
    # MAIL_PASSWORD = "cqxm dubb udpy nyvm"
    # MAIL_USE_TLS = True
    # MAIL_USE_SSL = False


config = {"development": DevelopmentConfig}
