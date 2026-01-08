from PyQt5.QtCore import QSettings

class Registry:
    def __init__(self, organization, application):
        self.settings = QSettings(organization, application)

    # ---------- GETTERS ----------
    def get(self, key, default=""):
        return self.settings.value(key, default, type=str)

    def get_int(self, key, default=0):
        return self.settings.value(key, default, type=int)

    def get_bool(self, key, default=False):
        return self.settings.value(key, default, type=bool)

    # ---------- SETTERS ----------
    def set(self, key, value):
        self.settings.setValue(key, str(value))

    def set_int(self, key, value):
        self.settings.setValue(key, int(value))

    def set_bool(self, key, value):
        self.settings.setValue(key, bool(value))