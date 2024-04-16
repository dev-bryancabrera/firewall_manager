import pymysql
from config import DevelopmentConfig


def get_connection():
    config = DevelopmentConfig
    return pymysql.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        db=config.MYSQL_DB,
        port=config.MYSQL_PORT,
    )
