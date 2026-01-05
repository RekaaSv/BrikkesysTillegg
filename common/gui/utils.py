import logging

from PyQt5.QtWidgets import QMessageBox


def show_message(tekst):
    logging.info("show_message")
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Info")
    msg.setText(tekst)
    msg.exec_()
