from PyQt5.QtCore import QSettings

# Application-wide settings
_settings = QSettings("Brikkesys", "BrikkesysTillegg")

def get_setting(key, default=None):
    return _settings.value(key, default)

def set_setting(key, value):
    _settings.setValue(key, value)

