from PyQt5.QtCore import QSettings

# Application-wide settings
_settings = QSettings("Brikkesys", "BrikkesysTillegg")

def get_setting(key, default=None):
    return _settings.value(key, default)

def set_setting(key, value):
    _settings.setValue(key, value)

# Konkrete lagringer i registry.
def get_trekkeplan_race_id():
    return get_setting("trekkeplan_race_id")

def put_trekkeplan_race_id(id):
    set_setting("trekkeplan_race_id", id)

def get_direkte_race_id():
    return get_setting("direkte_race_id")

def put_direkte_race_id(id):
    set_setting("direkte_race_id", id)

def get_eventor_api_key():
    return get_setting("faktura_race_id")

def put_eventor_api_key(id):
    set_setting("faktura_race_id", id)
