# from flask_bcrypt import check_password_hash
import bcrypt
from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, id, username, password_hash) -> None:
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @classmethod
    def check_password(self, hashed_password, password_hash):
        return bcrypt.checkpw(
            password_hash.encode("utf-8"), hashed_password.encode("utf-8")
        )
        # return check_password_hash(hashed_password, password_hash)
