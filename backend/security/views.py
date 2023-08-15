import json

from cryptography.fernet import Fernet
from config.settings import FERNET_KEY


class Security:
    f = Fernet(FERNET_KEY)

    def encrypt(self, value):
        return self.f.encrypt(self.__json_dumps(value).encode()).decode()

    def decrypt(self, value):
        return self.__json_loads(self.f.decrypt(value.encode()).decode())

    @staticmethod
    def __json_dumps(value):
        return json.dumps(value)

    @staticmethod
    def __json_loads(value):
        return json.loads(value)
