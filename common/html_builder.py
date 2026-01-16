import logging
import os
from decimal import Decimal


class HtmlBuilder:
    @staticmethod
    def ul(rows):
        """Lag en <ul>-liste med én kolonne"""
        html = "<ul>\n"
        for row in rows:
            html += f"  <li>{row[0]}</li>\n"
        html += "</ul>"
        return html

    @staticmethod
    def ol(rows):
        """Lag en <ol>-liste med én kolonne"""
        html = "<ol>\n"
        for row in rows:
            html += f"  <li>{row[0]}</li>\n"
        html += "</ol>"
        return html

    @staticmethod
    def table(rows, columns, border=1, sum_columns=None, sum_position="below"):
        logging.info("html_report.table")

        # fetchall() gir tuple → gjør om til liste
        rows = list(rows)

        # --- Summering ---
        total_row = None
        if sum_columns:
            total_row = sum_row(rows, sum_columns, len(columns))

            if sum_position == "above":
                rows.insert(0, total_row)
            else:
                rows.append(total_row)

        # --- HTML-start ---
        html = """
        <style>
            td.num {
                text-align: right;
                white-space: nowrap;
            }
            tr.totalrow td {
                font-weight: bold;
                border-top: 2px solid black;
                border-bottom: 2px solid black;
            }
        </style>
        """

        html += f"<table border='{border}'>\n  <tr>"

        # Kolonneoverskrifter
        for col in columns:
            html += f"<th>{col}</th>"
        html += "</tr>\n"

        # Rader
        for row in rows:
            is_total = (row is total_row)
            tr_class = " class='totalrow'" if is_total else ""
            html += f"<tr{tr_class}>"

            for cell in row:
                if isinstance(cell, (Decimal, float, int)):
                    form = format_cell(cell)
                    html += f"<td class='num'>{form}</td>\n"
                else:
                    html += f"<td>{cell}</td>\n"

            html += "</tr>\n"

        html += "</table>"
        return html

    @staticmethod
    def definition_list(rows, columns):
        """Lag en <dl> med første kolonne som <dt> og resten som <dd>"""
        html = "<dl>\n"
        for row in rows:
            html += f"  <dt>{row[0]}</dt>\n"
            for celle in row[1:]:
                html += f"  <dd>{celle}</dd>\n"
        html += "</dl>"
        return html

    @staticmethod
    def grouped_rows_in_single_table(
            rows, columns, group_by_index: int,
            report_header: str = ""):

        visningsindekser = [i for i in range(len(columns)) if i != group_by_index]

        html = f"""
        <style>
            /* PDF-toptekst som gjentas på hver side */
            @page {{
                margin: 10mm;
                margin-top: 20mm;
                @top-center {{
                    content: "{report_header}";
                    font-size: 24px;
                    font-weight: bold;
                }}
            }}
            @media print {{
                .html-header {{
                    display: none;
                }}
            }}

            /* HTML-header (vises kun i HTML-visning) */
            .html-header {{
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }}

            thead {{
                display: table-header-group;
            }}
            thead tr {{
                background-color: #e6e6e6;
            }}
            thead th {{
                font-size: 13pt;      /* eller 14pt hvis du vil ha det tydelig */
                font-weight: 600;     /* litt kraftigere enn normal bold */
                padding: 4px 3px;     /* litt mer luft rundt teksten */
            }}

            tbody.gruppe > tr:first-child > td {{
                padding-top: 0.8rem;
                font-weight: bold;
                font-size: 13pt;
            }}

            tr {{
                page-break-inside: avoid;
                line-height: 1.1;      /* tettere linjeavstand */
            }}

            td {{
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 12pt;
                padding: 1px 3px;      /* mindre luft rundt cellene */
            }}
            td.num {{
                text-align: right;
                white-space: nowrap;
            }}
        </style>

        <div class="html-header">{report_header}</div>

        <table>
            <thead>
                <tr>
        """

        # Kolonneheader
        for i in visningsindekser:
            html += f"<th>{columns[i]}</th>"
        html += "</tr></thead>\n"

        # Gruppering
        grupper = {}
        for row in rows:
            nøkkel = row[group_by_index]
            grupper.setdefault(nøkkel, []).append(row)

        # Generer grupper
        for nøkkel, group_rows in grupper.items():
            html += f'<tbody class="gruppe">\n'
#            html += f'  <tr><td colspan="{len(visningsindekser)}"><{heading_tag}>{nøkkel}</{heading_tag}></td></tr>\n'
            html += f'  <tr><td colspan="{len(visningsindekser)}">{nøkkel}</td></tr>\n'

            for row in group_rows:
                celler = []
                for i in visningsindekser:
                    verdi = row[i]
                    if isinstance(verdi, (Decimal, float, int)):
                        form = format_cell(verdi)
                        celler.append(f"<td class='num'>{form}</td>")
                    else:
                        celler.append(f"<td>{verdi}</td>")
                html += "  <tr>" + "".join(celler) + "</tr>\n"

            html += "</tbody>\n"

        html += "</table>"
        return html


    @staticmethod
    def download(html, file_name):
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        path = os.path.join(downloads_path, file_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        # Open file.
        os.startfile(path)

def format_cell(value):
    # Tall med tusenskilletegn (norsk stil)
    if isinstance(value, int):
        return f"{value:,}".replace(",", " ")
    if isinstance(value, float) or isinstance(value, Decimal):
        s = f"{value:,.2f}".replace(",", " ")
        return s.replace(".", ",")
    return value

def sum_row(rows, sum_columns, num_columns):
    """Returner en totals-rad basert på valgte kolonner."""
    totals = {}

    # Beregn summer
    for col in sum_columns:
        totals[col] = sum(
            float(r[col]) for r in rows
            if r[col] not in ("", None)
        )

    # Bygg totals-raden
    total_row = []
    for i in range(num_columns):
        if i in totals:
            total_row.append(totals[i])
        else:
            total_row.append("")

    return total_row
