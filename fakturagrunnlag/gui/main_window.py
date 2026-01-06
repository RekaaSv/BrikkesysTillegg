import logging

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QMenu, QAction, QPushButton, QLabel, QSizePolicy,
    QDialog, QMessageBox, QLineEdit,
    QProgressDialog, QApplication, QFrame
)
from PyQt5.QtCore import Qt

from common.settings import set_setting, get_setting
from fakturagrunnlag.control import control
from fakturagrunnlag.db import sql
from common.connection import ConnectionManager
from common.gui.utils import show_message, populate_table
from fakturagrunnlag.gui.create_bundle_dialog import CreateBundleDialog
from common.gui.common_table_item import CommonTableItem
from common.select_race_dialog import SelectRaceDialog


class FakturaMainWindow(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

        self.col_widths_bundles = [80, 120, 400, 80, 100, 200]
        self.col_widths_orders = [0, 60, 0, 0, 60, 150, 120, 120, 60, 80, 60, 200, 90, 80, 120]
        self.col_widths_lines = [0, 0, 0, 100, 220, 100, 0, 200, 0, 80, 200, 80, 120]

        self.eventor_apikey = None

        self.setWindowTitle("Fakturagrunnlag")
        self.resize(1500, 750)

        self.selected_bundle_id = None
        self.selected_order_id = None

        self.init_ui()

        self.make_layout()


    def init_ui(self):

        self.reload_btn = QPushButton("Last klubber fra Eventor")
        self.reload_btn.setToolTip("Les inn klubbene fra Eventor på nytt (i tilfelle endringer).")
        self.reload_btn.clicked.connect(self.reload_customers_with_key)

        self.new_bundle_btn = QPushButton("Ny ordrebunt")
        self.new_bundle_btn.setToolTip("Lag en ny ordrebunt.")
        self.new_bundle_btn.clicked.connect(self.create_bundle)

        self.close_button = QPushButton("Avslutt")
        self.close_button.clicked.connect(self.close)

        self.amountPerClubButton = QPushButton("Beløp pr klubb")
        self.amountPerClubButton.setToolTip("Liste som viser beløp pr. klubb.")
        self.amountPerClubButton.clicked.connect(self.make_amount_per_club)

        self.amountPerClubProductButton = QPushButton("Beløp pr klubb, produkt")
        self.amountPerClubProductButton.setToolTip("Liste som viser beløp pr. klubb og produkt.")
        self.amountPerClubProductButton.clicked.connect(self.make_amount_per_club_product)

        self.amountPerProductButton = QPushButton("Beløp pr produkt")
        self.amountPerProductButton.setToolTip("Liste som viser beløp pr. produkt.")
        self.amountPerProductButton.clicked.connect(self.make_amount_per_product)

        self.amountPerProductClubButton = QPushButton("Beløp pr produkt, klubb")
        self.amountPerProductClubButton.setToolTip("Liste som viser beløp pr. produkt og klubb.")
        self.amountPerProductClubButton.clicked.connect(self.make_amount_per_product_club)

        self.amountPerRaceProduct = QPushButton("Beløp pr løp, produkt")
        self.amountPerRaceProduct.setToolTip("Liste som viser beløp pr. løp og produkt.")
        self.amountPerRaceProduct.clicked.connect(self.make_amount_per_race_product)

        self.bundle_table = QTableWidget()
        self.order_table = QTableWidget()
        self.line_table = QTableWidget()

        self.bundle_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.order_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.line_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.bundle_table.setSortingEnabled(True)
        self.order_table.setSortingEnabled(True)
        self.line_table.setSortingEnabled(True)

        self.bundle_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.order_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.line_table.setContextMenuPolicy(Qt.CustomContextMenu)

        self.bundle_table.verticalHeader().setVisible(False)
        self.order_table.verticalHeader().setVisible(False)
        self.line_table.verticalHeader().setVisible(False)

        self.bundle_table.setWordWrap(False)
        self.order_table.setWordWrap(False)
        self.line_table.setWordWrap(False)

        self.bundle_table.customContextMenuRequested.connect(self.bundle_menu)
        self.order_table.customContextMenuRequested.connect(self.order_menu)
        self.line_table.customContextMenuRequested.connect(self.line_menu)

        self.bundle_table.setSelectionMode(QTableWidget.SingleSelection)
        self.bundle_table.setSelectionBehavior(QTableWidget.SelectRows)
#        self.order_table.setSelectionMode(QTableWidget.SingleSelection)
        self.order_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.line_table.setSelectionMode(QTableWidget.SingleSelection)
        self.line_table.setSelectionBehavior(QTableWidget.SelectRows)

        self.bundle_table.itemSelectionChanged.connect(self.on_bundle_selected)
        self.order_table.itemSelectionChanged.connect(self.on_order_selected)

        self.bundle_table.setMouseTracking(True)

#        self.make_layout()

        self.load_bundles()

    def make_layout(self):
        #
        # Layout
        #
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        center_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()

        center_frame = QFrame()
        center_frame.setFrameShape(QFrame.StyledPanel)
        center_frame.setFrameShadow(QFrame.Plain)
        center_frame.setLayout(center_layout)
        bottom_frame = QFrame()
        bottom_frame.setFrameShape(QFrame.StyledPanel)
        bottom_frame.setFrameShadow(QFrame.Plain)
        bottom_frame.setLayout(bottom_layout)


        main_layout.addLayout(top_layout)
        main_layout.addWidget(center_frame)
#        main_layout.addLayout(center_layout)
        main_layout.addWidget(bottom_frame)

        top_layout.addWidget(self.reload_btn)
        top_layout.addWidget(self.new_bundle_btn)
        top_layout.addStretch()

        bundle_layout = QVBoxLayout()
        order_layout = QVBoxLayout()
        line_layout = QVBoxLayout()

        center_layout.addLayout(bundle_layout)
        center_layout.addLayout(order_layout)
        center_layout.addLayout(line_layout)


        bundle_layout.addWidget(self.bundle_table)
        bundle_layout.addStretch()

        order_layout.addWidget(self.order_table)
        order_layout.addStretch()

        line_layout.addWidget(self.line_table)
        line_layout.addStretch()

        bottom_layout.addWidget(self.amountPerClubButton)
        bottom_layout.addWidget(self.amountPerClubProductButton)
        bottom_layout.addWidget(self.amountPerProductButton)
        bottom_layout.addWidget(self.amountPerProductClubButton)
        bottom_layout.addWidget(self.amountPerRaceProduct)

        bottom_layout.addStretch()
        bottom_layout.addWidget(self.close_button)


        self.setLayout(main_layout)

        """
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.reload_btn)
        top_bar.addStretch()
        layout = QVBoxLayout(self)
        layout.addLayout(top_bar)


        splitter = QSplitter(Qt.Vertical)

        splitter.addWidget(self.bundle_table)
        splitter.addWidget(self.order_table)
        splitter.addWidget(self.line_table)
        """
    def load_bundles(self):
        logging.info("load_bundles")
        rows, columns = sql.select_bundles(self.ctx.conn_mgr)
        self.populate_my_table(self.bundle_table, columns, rows)
#        self.bundle_table.setColumnHidden(2, True)
        self.set_table_sizes(self.bundle_table, self.col_widths_bundles, 150)

    def load_orders(self, bundle_id):
        logging.info("load_orders")
        invoice_config = self.ctx.config["fakturering"]
        order_no_base = invoice_config.getint("ordrenummer_start", fallback=100000)
        customer_no_base = invoice_config.getint("kundenummer_start", fallback=100000)

        rows, columns = sql.select_orders(self.ctx.conn_mgr, bundle_id, order_no_base, customer_no_base)
        self.populate_my_table(self.order_table, columns, rows)
        self.order_table.setColumnHidden(0, True)
        self.order_table.setColumnHidden(2, True)
        self.order_table.setColumnHidden(3, True)
        self.set_table_sizes(self.order_table, self.col_widths_orders, 400)

    def load_lines(self, order_id):
        logging.info("load_orders")
        rows, columns = sql.select_order_lines(self.ctx.conn_mgr, order_id)
        self.populate_my_table(self.line_table, columns, rows)
        self.line_table.setColumnHidden(0, True)
        self.line_table.setColumnHidden(1, True)
        self.line_table.setColumnHidden(2, True)
        self.line_table.setColumnHidden(6, True)
        self.line_table.setColumnHidden(8, True)
        self.set_table_sizes(self.line_table, self.col_widths_lines, 300)

    def bundle_menu(self, pos):
        menu = QMenu()
        new_bundle = QAction("Opprett ny ordrebunt", self)
        add_race = QAction("Legg til løp", self)
#        add_org_no = QAction("Legg på organisasjonsnummer (kun for EHF faktura)", self)
        export_csv = QAction("Eksporter til Tripletex CSV", self)
        export_excel = QAction("Eksporter til Tripletex Excel", self)
        remove_race = QAction("Ta vekk løp", self)
        delete_bundle = QAction("Slett ordrebunt", self)

        new_bundle.triggered.connect(self.create_bundle)
        add_race.triggered.connect(self.add_race_to_bundle)
#        add_org_no.triggered.connect(self.add_org_no)
        remove_race.triggered.connect(self.remove_race_from_bundle)
        export_csv.triggered.connect(self.export_bundle_csv)
        export_excel.triggered.connect(self.export_bundle_excel)
        delete_bundle.triggered.connect(self.delete_this_bundle)

        menu.addAction(new_bundle)
        menu.addAction(add_race)
#        menu.addAction(add_org_no)
        menu.addAction(export_csv)
        menu.addAction(export_excel)
        menu.addAction(remove_race)
        menu.addAction(delete_bundle)
        menu.exec_(self.bundle_table.mapToGlobal(pos))

    def order_menu(self, pos):
        menu = QMenu()
        dont_export_order = QAction("Snu (av/på) 'Eksport'", self)
        make_order_word = QAction("Last ned ordre (Word)", self)
        make_order_pdf = QAction("Last ned ordre (PDF)", self)
        dont_export_order.triggered.connect(self.dont_export_on_off)
        make_order_word.triggered.connect(self.make_order_word)
        make_order_pdf.triggered.connect(self.make_order_pdf)
        menu.addAction(dont_export_order)
        menu.addAction(make_order_pdf)
        menu.addAction(make_order_word)
        menu.exec_(self.order_table.mapToGlobal(pos))

    def line_menu(self, pos):
        menu = QMenu()
        menu.exec_(self.line_table.mapToGlobal(pos))

    def create_bundle(self):
        dlg = CreateBundleDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            values = dlg.get_values()
            try:
                sql.cre_order_bundle(
                    self.ctx.conn_mgr,
                    values["order_date"],
                    values["remark"],
                    values["currency"]
                )
                QMessageBox.information(self, "Ordrebunt", "Ordrebunt ble opprettet.")
                self.load_bundles()
            except Exception as e:
                QMessageBox.critical(self, "Feil", f"Kunne ikke opprette ordrebunt:\n{e}")
                raise

    def add_race_to_bundle(self):
        bundle_id = self.get_selected_bundle_id()
        if bundle_id is None:
            return

        # 2. Åpne dialog for å velge løp
        dlg = SelectRaceDialog(self.ctx, self)
        if dlg.exec_() == QDialog.Accepted:
            raceid = dlg.selected_race_id
            if not raceid:
                QMessageBox.warning(self, "Ingen løp valgt", "Du må velge et løp.")
                return
            if dlg.selected_bundle != None:
                QMessageBox.warning(self, "Løp allerede valgt", f"Løp {raceid} er allerede med i bunt {str(dlg.selected_bundle)}")
                return

            # 3. Utfør legg-løp-til-bunten.
            try:
                count_orders, count_lines = control.add_race_to_bundle(self, bundle_id, raceid)

                show_message(f"Løp {raceid} lagt til bunt {bundle_id} med {count_orders} nye ordrer og {count_lines} nye ordrelinjer")

                self.load_bundles()
                self.select_bundle_by_id(bundle_id)
            except Exception as e:
                QMessageBox.critical(self, "Feil", f"Klarte ikke legge til løp:\n{e}")
                raise

    def select_bundle_by_id(self, bundle_id):
        # Antar at kolonne 0 inneholder id
        self.bundle_table.clearSelection()
        for row in range(self.bundle_table.rowCount()):
            item = self.bundle_table.item(row, 0)
            if item and int(item.text()) == int(bundle_id):
                self.bundle_table.selectRow(row)
                self.bundle_table.scrollToItem(item)
                break

    def remove_race_from_bundle(self):
        bundle_id = self.get_selected_bundle_id()
        if bundle_id is None:
            return

        # 2. Åpne dialog for å velge løp
        dlg = SelectRaceDialog(self.ctx, self)
        if dlg.exec_() == QDialog.Accepted:
            raceid = dlg.selected_race_id
            if not raceid:
                QMessageBox.warning(self, "Ingen løp valgt", "Du må velge et løp.")
                return

            if dlg.selected_bundle != int(bundle_id):
                QMessageBox.warning(self, "Feil løp valgt",
                                    f"Løp {raceid} er ikke med i bunt {bundle_id}")
                return

            # 3. Utfør fjern-løp-fra-bunten.
            try:
                count_orders, count_lines = control.remove_race_from_bundle(self, bundle_id, raceid)
                show_message(f"Løp {raceid} fjernet fra bunt {bundle_id}. {count_orders} ordrer fjernet, {count_lines} ordrelinjer fjernet")

                self.load_bundles()
                self.select_bundle_by_id(bundle_id)

            except Exception as e:
                QMessageBox.critical(self, "Feil", f"Klarte ikke fjerne løp:\n{e}")
                raise


    def delete_this_bundle(self):
        logging.info("delete_this_bundle")
        bundle_id = self.get_selected_bundle_id()
        if bundle_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Bekreft sletting",
            f"Er du sikker på at du vil slette bunt {bundle_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            control.delete_bundle(self, bundle_id)
        else:
            # Avbryt
            return

    def add_org_no(self):
        bundle_id = self.get_selected_bundle_id()
        if bundle_id is None:
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Organisasjonsnummer")

        layout = QVBoxLayout(dlg)
        confirm_btn = QPushButton("Start import fra Brønnøysund register")
        layout.addWidget(confirm_btn)

        def start_org_import():
            dlg.accept()

            progress = QProgressDialog("Slår opp ...", None, 0, 0, self)
            progress.setWindowModality(Qt.ApplicationModal)
            progress.setWindowTitle("Import av Org.nr fra Brønnøysund")
            progress.setMinimumDuration(0)
#            progress.setCancelButton(None)
            progress.show()
            QApplication.processEvents()

            try:
                no_of_orgnr = control.add_org_no(self, bundle_id, progress)
            except ValueError as ve:
                progress.close()
                show_message(str(ve))
            except Exception as e:
                progress.close()
                show_message(str(e))
            else:
                progress.close()
                show_message("Antall org.nr importert: " + str(no_of_orgnr))

        confirm_btn.clicked.connect(start_org_import)
        dlg.exec_()


    def export_bundle_csv(self):
        bundle_id = self.get_selected_bundle_id()
        if bundle_id is None:
            return
        noof_rows = control.export_tripletex_csv(self, bundle_id)
        show_message(f"Antall ordrelinjer lastet ned til 'Downloads'-mappen: {noof_rows}.")

    def export_bundle_excel(self):
        bundle_id = self.get_selected_bundle_id()
        if bundle_id is None:
            return
        noof_rows = control.export_tripletex_excel(self, bundle_id)
        show_message(f"Antall ordrelinjer lastet ned til 'Downloads'-mappen: {noof_rows}.")

    def dont_export_on_off(self):
        logging.info("dont_export_on_off")
        selected_model_rows = self.order_table.selectionModel().selectedRows()
        if not selected_model_rows:
            show_message("Du må velge minst en rad!")
            return
        for index in selected_model_rows:
            row_ix = index.row()
            item = self.order_table.item(row_ix, 0)
            order_id = int(item.text())
            sql.toggle_dont_export(self.ctx.conn_mgr, order_id)

        bundle_id = self.get_selected_bundle_id()
        self.select_bundle_by_id(bundle_id)


    def delete_bundle(self):
        # TODO: Delete from invoice_bundles and cascade
        pass

    def make_order_word(self):
        order_no = self.get_selected_order_id()
        if order_no is None:
            return

        invoice_config = self.ctx.config["fakturering"]

        control.make_order_word(self, invoice_config, order_no)

    def make_order_pdf(self):
        order_no = self.get_selected_order_id()
        if order_no is None:
            return

        invoice_config = self.ctx.config["fakturering"]

        control.make_order_pdf(self, invoice_config, order_no)

    def map_invoice_row(self, row_data):
        return [CommonTableItem.from_value(v) for v in row_data]

    def invoice_cell_postprocessor(self, table, row_idx, col_idx, item):
        # Checkbox i order_table
        if table == self.order_table and col_idx == 13:
            value = item.sort_value
            item.setCheckState(Qt.Checked if value == 0 else Qt.Unchecked)
            item.setText("")
            item.setFlags(item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsEnabled)

        # Tooltip i bundle_table
        if table == self.bundle_table and col_idx == 2:
            item.setToolTip(item.text())

    def populate_my_table(self, table, columns: list[any], rows):
        logging.debug("populate_my_table")
        populate_table(
            table,
            columns,
            rows,
            self.map_invoice_row,
            self.invoice_cell_postprocessor
        )

    def on_bundle_selected(self):
        logging.info("on_bundle_selected")
        selected = self.bundle_table.selectionModel().selectedRows()
        if not selected:
            self.line_table.setRowCount(0)
            self.order_table.setRowCount(0)
            return
        selected_row_id = selected[0].row()
        self.selected_bundle_id = self.bundle_table.item(selected_row_id, 0).text()
        self.load_orders(self.selected_bundle_id)
        self.line_table.clearContents()
        self.line_table.setRowCount(0)

    def on_order_selected(self):
        logging.info("on_order_selected")
        selected = self.order_table.selectionModel().selectedRows()
        if not selected:
            self.line_table.setRowCount(0)
            return
        selected_row_id = selected[0].row()
        self.selected_order_id = self.order_table.item(selected_row_id, 0).text()
        self.load_lines(self.selected_order_id)

    def put_apikey_in_registry(self, api_key: str):
        set_setting("API-key", api_key)

    def get_apikey_from_registry(self) -> str | None:
        value = get_setting("API-key")
        return str(value) if value is not None else ""

    def reload_customers_with_key(self):
        self.eventor_apikey = self.get_apikey_from_registry()
        dlg = QDialog(self)
        dlg.setWindowTitle("Importer klubber fra Eventor")

        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel("Skriv inn Eventor API-key:"))

        api_input = QLineEdit()
        api_input.setText(self.eventor_apikey)
#        api_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(api_input)

        confirm_btn = QPushButton("Start import")
        layout.addWidget(confirm_btn)

        def start_import():
            new_key = api_input.text().strip()
            if not new_key:
                show_message("Du må angi Eventor sin API-key. Prøv igjen!")
                return
            dlg.accept()

            progress = QProgressDialog("Laster klubber fra Eventor...", None, 0, 0, self)
            progress.setWindowModality(Qt.ApplicationModal)
            progress.setWindowTitle("Import pågår")
            progress.setMinimumDuration(0)
            progress.setCancelButton(None)
            progress.show()
            QApplication.processEvents()

            try:
                no_of_clubs = control.import_eventor_clubs(self, new_key, progress)
            except ValueError as ve:
                progress.close()
                show_message(str(ve))
            except Exception as e:
                progress.close()
                show_message(str(e))
            else:
                if new_key != self.eventor_apikey:
                    self.eventor_apikey = new_key
                    self.put_apikey_in_registry(self.eventor_apikey)

                progress.close()
                show_message("Antall klubber importert: " + str(no_of_clubs))

        confirm_btn.clicked.connect(start_import)
        dlg.exec_()

    def set_table_sizes(self, table, col_sizes, max_height=600):
        self.set_fixed_widths(table, col_sizes)
        table.resizeRowsToContents()
        self.adjust_table_hight(table, max_height)
        self.adjust_table_width(table)

    def set_fixed_widths(self, table, widths):
        for col_inx, width in enumerate(widths):
            table.setColumnWidth(col_inx, width)

    def adjust_table_hight(self, table, max_height = 600):
        logging.info("adjust_table_hight")
        header_h = table.horizontalHeader().height()
        row_height = header_h
        scrollbar_h = table.horizontalScrollBar().height() if table.horizontalScrollBar().isVisible() else 0
        total_height = header_h + (row_height * table.rowCount()) + scrollbar_h + 2  # +2 for ramme
        limited_height = min(total_height, max_height)
        table.setFixedHeight(limited_height)


    def adjust_table_width(self, table, extra_margin=2):
        logging.info("adjust_table_width")
        total_width = sum(table.columnWidth(kol) for kol in range(table.columnCount()))
        vertical_scroll = table.verticalScrollBar().sizeHint().width() # if table.verticalScrollBar().isVisible() else 0
        frame = table.frameWidth() * 2
        table.setFixedWidth(total_width + vertical_scroll + frame + extra_margin)
        logging.debug("vertical_scroll: %s", vertical_scroll)

    def get_selected_bundle_id(self):
        selected = self.bundle_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ingen bunt valgt", "Velg en bunt først.")
            return
        index = selected[0]  # antar én valgt rad, celle 0.
        bundle_id = self.bundle_table.model().data(index)
        if not bundle_id:
            QMessageBox.warning(self, "Ugyldig valg", "Klarte ikke hente bunt-ID.")
        return bundle_id

    def get_selected_order_id(self):
        selected = self.order_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ingen ordre valgt", "Velg en ordre først.")
            return
        index = selected[0]  # antar én valgt rad
        order_id = self.order_table.model().data(index)
        if not order_id:
            QMessageBox.warning(self, "Ugyldig valg", "Klarte ikke hente ordrenr.")
        return order_id

    def adjust_table_width(self, table, extra_margin=2):
        logging.info("adjust_table_width")
        total_width = sum(table.columnWidth(kol) for kol in range(table.columnCount()))
        vertical_scroll = table.verticalScrollBar().sizeHint().width() # if table.verticalScrollBar().isVisible() else 0
        frame = table.frameWidth() * 2
        table.setFixedWidth(total_width + vertical_scroll + frame + extra_margin)
        logging.debug("vertical_scroll: %s", vertical_scroll)

    def get_order_no_base(self):
        invoice_config = self.ctx.config["fakturering"]
        return invoice_config.getint("ordrenummer_start", fallback=100000)

    def get_customer_no_base(self):
        invoice_config = self.ctx.config["fakturering"]
        return invoice_config.getint("kundenummer_start", fallback=100000)

    def make_amount_per_club(self):
        logging.info("make_amount_per_club")
        invoice_config = self.ctx.config["fakturering"]
        order_no_base = invoice_config.getint("ordrenummer_start", fallback=100000)
        customer_no_base = invoice_config.getint("kundenummer_start", fallback=100000)
        bundle_id = self.get_selected_bundle_id()
        if bundle_id:
            control.make_amount_per_club(self, bundle_id, order_no_base, customer_no_base)

    def make_amount_per_club_product(self):
        logging.info("make_amount_per_club_product")
        invoice_config = self.ctx.config["fakturering"]
        order_no_base = invoice_config.getint("ordrenummer_start", fallback=100000)
        customer_no_base = invoice_config.getint("kundenummer_start", fallback=100000)
        bundle_id = self.get_selected_bundle_id()
        if bundle_id:
            control.make_amount_per_club_product(self, bundle_id, order_no_base, customer_no_base)

    def make_amount_per_product(self):
        logging.info("make_amount_per_product")
        invoice_config = self.ctx.config["fakturering"]
        order_no_base = invoice_config.getint("ordrenummer_start", fallback=100000)
        customer_no_base = invoice_config.getint("kundenummer_start", fallback=100000)
        bundle_id = self.get_selected_bundle_id()
        if bundle_id:
            control.make_amount_per_product(self, bundle_id, order_no_base, customer_no_base)

    def make_amount_per_product_club(self):
        logging.info("make_amount_per_product_club")
        invoice_config = self.ctx.config["fakturering"]
        order_no_base = invoice_config.getint("ordrenummer_start", fallback=100000)
        customer_no_base = invoice_config.getint("kundenummer_start", fallback=100000)
        bundle_id = self.get_selected_bundle_id()
        if bundle_id:
            control.make_amount_per_product_club(self, bundle_id, order_no_base, customer_no_base)

    def make_amount_per_race_product(self):
        logging.info("make_amount_per_race_product")
        invoice_config = self.ctx.config["fakturering"]
        bundle_id = self.get_selected_bundle_id()
        if bundle_id:
            control.make_amount_per_race_product(self, bundle_id)

