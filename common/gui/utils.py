import logging

from PyQt5.QtWidgets import QMessageBox, QSizePolicy


def show_message(tekst):
    logging.info("show_message")
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Info")
    msg.setText(tekst)
    msg.exec_()

def populate_table(table, columns, rows, row_mapper, cell_postprocessor=None):
    logging.debug("populate_table")

    table.clearContents()

    is_sorted = table.isSortingEnabled()
    if is_sorted:
        table.setSortingEnabled(False)

    table.setColumnCount(len(columns))
    table.setRowCount(len(rows))
    table.setHorizontalHeaderLabels(columns)

    for row_idx, row_data in enumerate(rows):
        items = row_mapper(row_data)

        for col_idx, item in enumerate(items):
            # Modulspesifikk cell-behandling
            if cell_postprocessor:
                cell_postprocessor(table, row_idx, col_idx, item, row_data[col_idx])

            table.setItem(row_idx, col_idx, item)

    if is_sorted:
        table.setSortingEnabled(True)

    table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    logging.info("populate_table end")