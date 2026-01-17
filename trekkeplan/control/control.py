import datetime
import logging
import os

from weasyprint import CSS

from common.html_builder import HtmlBuilder
from common.gui.utils import show_message, set_table_sizes
from trekkeplan.db import sql
from weasyprint import HTML

def first_start_edited(parent, race_id, new_first_start_datetime):
    logging.info("control.first_start_edited")
    # Update first start-time, then rebuild redundant columns in class_starts.
    sql.upd_first_start(parent.ctx.conn_mgr, race_id, new_first_start_datetime)
    logging.debug("control.first_start_edited new_first_start_datetime: %s", new_first_start_datetime)
    parent.race['first_start'] = new_first_start_datetime

    rebuild_class_starts(parent, race_id)

def delete_class_start_row(parent, race_id, classstart_id):
    logging.info("control.delete_class_start_row")
    sql.delete_class_start_row(parent.ctx.conn_mgr, race_id, classstart_id)
    rebuild_class_starts(parent, race_id)

def class_start_down_up(parent, id, step):
    logging.info("control.class_start_down_up")
    sql.class_start_down_up(parent.ctx.conn_mgr, id, step)
    rebuild_class_starts(parent, parent.race_id)

def delete_class_start_rows(parent, race_id, blocklag_id):
    logging.info("control.delete_class_start_rows")
    sql.delete_class_start_rows(parent.ctx.conn_mgr, race_id, blocklag_id)
    rebuild_class_starts(parent, race_id)

def delete_class_start_all(parent, race_id):
    logging.info("control.delete_class_start_all")
    sql.delete_class_start_all(parent.ctx.conn_mgr, race_id)
    rebuild_class_starts(parent, race_id)

def delete_blocklag(parent, race_id, blocklag_id, blockId):
    logging.info("control.delete_blocklag")
    returned = sql.delete_blocklag(parent.ctx.conn_mgr, race_id, blocklag_id)
    if returned:
        # Prøv å slett bås også.
        returned2 = sql.delete_block(parent.ctx.conn_mgr, race_id, blockId)
        if returned2: logging.info("delete_block slettet OK")
        return None
    else:
        return "Fjern tilhørende klasser fra planen, og prøv igjen!"

def insert_class_start_nots(parent, race_id, classsIds):
    logging.info("control.insert_class_start_nots")
    for classid in classsIds:
        sql.insert_class_start_not(parent.ctx.conn_mgr, race_id, classid)

def delete_class_start_not(parent, race_id):
    logging.info("control.delete_class_start_not")
    sql.delete_class_start_not(parent.ctx.conn_mgr, race_id)


def add_block_lag(parent, race_id, block, lag, gap):
    logging.info("control.add_block_lag")
    blockid = sql.add_block(parent.ctx.conn_mgr, race_id, block)
    sql.add_blocklag(parent.ctx.conn_mgr, blockid, lag, gap)


def add_lag(parent, blockid, lag, gap):
    logging.info("control.add_lag")
    sql.add_blocklag(parent.ctx.conn_mgr, blockid, lag, gap)

def insert_class_start(parent, race_id, blocklag_id, class_id, timegap, sortorder):
    logging.info("control.insert_class_start")
    sql.insert_class_start(parent.ctx.conn_mgr, race_id, blocklag_id, class_id, timegap, sortorder)


def refresh_table(parent, table):
    logging.info("control.refresh_table")
    max_next_time = None # For table_block_lag returneres max_next_time
    if table == parent.table_not_planned:
        logging.info("control.refresh_table table_not_planned")
        rows, columns = sql.read_not_planned(parent.ctx.conn_mgr, parent.race_id)
        col_widths = parent.col_widths_not_planned
    elif table == parent.table_block_lag:
        logging.info("control.refresh_table table_block_lag")
        rows, columns = sql.read_block_lags(parent.ctx.conn_mgr, parent.race_id)
        max_next_time = parent.max_value(rows, 5)
        logging.debug("control.refresh_table max_next_time: %s", max_next_time)
        col_widths = parent.col_widths_block_lag
    elif table == parent.table_class_start:
        logging.info("control.refresh_table table_class_start")
        rows, columns = sql.read_class_starts(parent.ctx.conn_mgr, parent.race_id)
        col_widths = parent.col_widths_class_start
    else:
        logging.error("Systemfeil!", exc_info=True)
        raise Exception("Systemfeil!")

    parent.populate_my_table(table, columns, rows)
    set_table_sizes(table, col_widths)
    return max_next_time

def class_start_free_updated(parent, race_id, classstartid, blocklagid, new_value, cellno):
    logging.info("control.class_start_free_updated")
    logging.info("Signal av")
    parent.table_class_start.blockSignals(True)
    if cellno==1:
        sql.upd_class_start_free_before(parent.ctx.conn_mgr, race_id, classstartid, new_value)
    elif cellno==2:
        sql.upd_class_start_free_after(parent.ctx.conn_mgr, race_id, classstartid, new_value)
    # Rebuild
    rebuild_class_starts(parent, race_id)
    refresh_table(parent, parent.table_class_start)

    parent.after_plan_changed(blocklagid)

    parent.table_class_start.blockSignals(False)
    logging.debug("control.class_start_free_updated end")

def make_startlist(parent, race_id):
    logging.info("control.make_startlist")
    rows, columns = sql.sql_start_list(parent.ctx.conn_mgr, race_id)

    report_header = f"{parent.race['day']}  {parent.race['name']}    -   Startliste"
    css = HtmlBuilder.report_css(report_header)
    html = HtmlBuilder.grouped_rows_in_single_table(rows, columns, 0, report_header, css=css)
    html = HtmlBuilder.build_report_html(css, html)

    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    path = os.path.join(downloads_path, "startliste.pdf")

    HTML(string=html).write_pdf(path)
    os.startfile(path)

#    HtmlBuilder.download(html, "Startlist.html")

def make_starterlist(parent, race_id):
    logging.info("control.make_starterlist")
    rows, columns = sql.sql_starter_list(parent.ctx.conn_mgr, race_id)
    report_header = f"{parent.race['day']}  {parent.race['name']} - Starter-liste"
    css = HtmlBuilder.report_css(report_header)
    html = HtmlBuilder.grouped_rows_in_single_table(rows, columns, 5, report_header, css=css)
    html = HtmlBuilder.build_report_html(css, html)

    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    path = os.path.join(downloads_path, "startliste.pdf")
    HTML(string=html).write_pdf(path)
    os.startfile(path)

    HtmlBuilder.download(html, "Starterlist.html")

def make_noof_in_cource(parent, race_id):
    logging.info("control.make_noof_in_cource")
    rows, columns = sql.sql_noof_in_cource(parent.ctx.conn_mgr, race_id)
    report_header = f"{parent.race['day']}  {parent.race['name']} - Antall pr. løype"
    css = HtmlBuilder.report_css(report_header)
    html = HtmlBuilder.grouped_rows_in_single_table(rows, columns, 0, report_header, css=css)
    html = HtmlBuilder.build_report_html(css, html)

    HtmlBuilder.download(html, "Løypeliste.html")

def make_noof_in_control1(parent, race_id):
    logging.info("control.make_noof_in_control1")
    rows, columns = sql.sql_noof_in_control1(parent.ctx.conn_mgr, race_id)

    report_header = f"{parent.race['day']}  {parent.race['name']} - Antall pr. post 1"
    css = HtmlBuilder.report_css(report_header)
    html = HtmlBuilder.grouped_rows_in_single_table(rows, columns, 0, report_header, css=css)
    html = HtmlBuilder.build_report_html(css, html)

    HtmlBuilder.download(html, "Post1list.html")

def make_same_time_cource(parent, race_id):
    logging.info("control.make_same_time_cource")
    rows, columns = sql.sql_same_time_cource(parent.ctx.conn_mgr, race_id)
    report_header = f"{parent.race['day']}  {parent.race['name']} - Samtidige i løype"
    css = HtmlBuilder.report_table_css()
#    css = ""
    html = HtmlBuilder.table(rows, columns, report_header)
    html = HtmlBuilder.build_report_html(css, html)

    HtmlBuilder.download(html, "SamtidigeILøype.html")

def make_same_time_control1(parent, race_id):
    logging.info("control.make_same_time_control1")
    rows, columns = sql.sql_same_time_control1(parent.ctx.conn_mgr, race_id)
    report_header = f"{parent.race['day']}  {parent.race['name']} - Samtidige post 1"
    css = HtmlBuilder.report_table_css()
    html = HtmlBuilder.table(rows, columns, report_header)
    html = HtmlBuilder.build_report_html(css, html)

    HtmlBuilder.download(html, "SamtidigeTilPost1.html")

def draw_start_times(parent, race_id):
    sql.draw_start_times(parent.ctx.conn_mgr, race_id)
    now = datetime.datetime.now()
    # Sett tidsstempel på at det er trukket, både i basen og global variabel.
    sql.upd_draw_time(parent.ctx.conn_mgr, race_id, now)
    parent.race['draw_time'] = now

    show_message("Trekking foretatt, se Startliste!")

def clear_start_times(parent, race_id):
    sql.clear_start_times(parent.ctx.conn_mgr, race_id)
    show_message("Starttider fjernet, se Startliste!")

def rebuild_class_starts(parent, race_id):
    sql.rebuild_class_starts(parent.ctx.conn_mgr, race_id)

    # Sett tidsstempel på at planen er endret, både i basen og global variabel.
    now = datetime.datetime.now()
    sql.upd_drawplan_changed(parent.ctx.conn_mgr, race_id, now)
    parent.race['drawplan_changed'] = now
