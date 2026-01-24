MESSAGE_INFO_BG = "#e0f7fa"      # lys turkis – rolig info
MESSAGE_SUCCESS_BG = "#e8f5e9"   # lys grønn – OK / lagret
MESSAGE_WARNING_BG = "#fff3cd"   # lys gul – advarsel
MESSAGE_ERROR_BG = "#f8d7da"     # lys rød – feil

class MessageHandler:
    def __init__(self, message_bar):
        self.message_bar = message_bar

    def info(self, text, timeout=10000):
        self.message_bar.show_message(text, MESSAGE_INFO_BG, timeout)

    def success(self, text, timeout=10000):
        self.message_bar.show_message(text, MESSAGE_SUCCESS_BG, timeout)

    def warning(self, text, timeout=10000):
        self.message_bar.show_message(text, MESSAGE_WARNING_BG, timeout)

    def error(self, text, timeout=10000):
        self.message_bar.show_message(text, MESSAGE_ERROR_BG, timeout)
