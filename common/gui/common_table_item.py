from decimal import Decimal

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt, QCollator, QLocale
from datetime import datetime, date, time, timedelta

collator = QCollator()
collator.setLocale(QLocale(QLocale.Norwegian, QLocale.Norway))

class CommonTableItem(QTableWidgetItem):
    def __init__(self, display_text: str, sort_value, alignment: Qt.AlignmentFlag):
        super().__init__(display_text)
        self.setBackground(QColor("white"))
        self.setData(Qt.UserRole, sort_value)
        self.setTextAlignment(alignment)
        self.type = type(sort_value)

    def __lt__(self, other):
        if isinstance(other, QTableWidgetItem):
            a = self.data(Qt.UserRole)
            b = other.data(Qt.UserRole)
            if self.type == str:
                return collator.compare(a, b) < 0
            else:
                try:
                    return a < b
                except TypeError:
                    pass
            return super().__lt__(other)

    @classmethod
    def from_value(cls, value, time_only=False):
        """Velger visning, sorteringsverdi og justering basert på type. None vises som blankt."""
        if value is None:
            return cls("", "", Qt.AlignLeft | Qt.AlignVCenter)

        if isinstance(value, datetime):
            if time_only:
                return cls(value.strftime("%H:%M:%S"), value, Qt.AlignCenter)
            else:
                return cls(value.strftime("%Y-%m-%d %H:%M:%S"), value, Qt.AlignCenter)
        elif isinstance(value, date):
            return cls(value.strftime("%Y-%m-%d"), value, Qt.AlignCenter)
        elif isinstance(value, time):
            return cls(value.strftime("%H:%M:%S"), value, Qt.AlignCenter)
        elif isinstance(value, timedelta):
            total_seconds = int(value.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            if hours > 0:
                display = f"{hours}:{minutes:02}:{seconds:02}"
            else:
                display = f"{minutes}:{seconds:02}"
            return cls(display, value, Qt.AlignRight | Qt.AlignVCenter)
        elif isinstance(value, int):
            return cls(str(value), value, Qt.AlignRight | Qt.AlignVCenter)
        elif isinstance(value, Decimal):
            # Norsk format: to desimaler, komma som skilletegn
            text = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return cls(text, value, Qt.AlignRight | Qt.AlignVCenter)
        elif isinstance(value, float):
            text = f"{value:.2f}"
            return cls(text, value, Qt.AlignRight | Qt.AlignVCenter)
        elif isinstance(value, str):
            show_value = value
            if "\n" in value:
                show_value = value.split("\n", 1)[0] + " (se tooltip)"
            return cls(show_value, value.lower(), Qt.AlignLeft | Qt.AlignVCenter)
        else:
            return cls(str(value), str(value), Qt.AlignLeft | Qt.AlignVCenter)
