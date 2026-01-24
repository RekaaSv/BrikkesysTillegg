import logging

from PyQt5.QtWidgets import QMessageBox, QSizePolicy


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


def adjust_table_hight(table, max_height = 600):
    logging.info("adjust_table_hight")
    header_h = table.horizontalHeader().height()
    row_height = header_h
    scrollbar_h = table.horizontalScrollBar().height() if table.horizontalScrollBar().isVisible() else 0
    total_height = header_h + (row_height * table.rowCount()) + scrollbar_h + 2  # +2 for ramme
    limited_height = min(total_height, max_height)
    table.setFixedHeight(limited_height)


def adjust_table_width(table, extra_margin=2):
    logging.info("adjust_table_width")
    total_width = sum(table.columnWidth(kol) for kol in range(table.columnCount()))
    vertical_scroll = table.verticalScrollBar().sizeHint().width() # if table.verticalScrollBar().isVisible() else 0
    frame = table.frameWidth() * 2
    table.setFixedWidth(total_width + vertical_scroll + frame + extra_margin)
    logging.debug("vertical_scroll: %s", vertical_scroll)


def set_fixed_widths(table, widths):
    for col_inx, width in enumerate(widths):
        table.setColumnWidth(col_inx, width)


def set_table_sizes(table, col_sizes, max_height=600):
    set_fixed_widths(table, col_sizes)
    table.resizeRowsToContents()
    adjust_table_hight(table, max_height)
    adjust_table_width(table)

def set_table_widths(table, col_sizes):
    set_fixed_widths(table, col_sizes)
    table.resizeRowsToContents()
#    adjust_table_hight(table, max_height)
    adjust_table_width(table)

def ask_confirmation(self, message: str) -> bool:
    reply = QMessageBox.question(
        self,
        "Bekreft handling",
        message,
        QMessageBox.Ok | QMessageBox.Cancel,
        QMessageBox.Cancel
    )
    return reply == QMessageBox.Ok
