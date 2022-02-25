from cffi.backend_ctypes import unicode
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_id, username, password, staff_type):
        self.id = unicode(user_id)
        self.username = username
        self.password = password
        self.staff_type = staff_type
        self.authenticated = False

    def is_active(self):
        return self.is_active()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.id
