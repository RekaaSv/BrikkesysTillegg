from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
import logging


class PdfBuilder:

    @staticmethod
    def build_startlist_pdf(msg, rows, columns, group_col, report_header, file_name):
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        path = os.path.join(downloads_path, file_name)

        try:
            styles = getSampleStyleSheet()

            # Kolonne 0 brukes kun i gruppeheader → tabellen har 5 kolonner
            visible_columns = [col for i, col in enumerate(columns) if i != group_col]

            # Eksakte bredder for de 5 synlige kolonnene
            col_widths = [37, 187, 187, 74, 74]

            # Header-funksjon for hver side
            def draw_header(canvas, doc):
                page_width, page_height = canvas._pagesize

                # Fast topp-posisjon for header (stabil på alle sider)
                header_top = page_height - 20

                # --- Rapportnavn (kun første side) ---
                if canvas.getPageNumber() == 1:
                    canvas.setFont("Helvetica-Bold", 16)
                    canvas.drawString(doc.leftMargin, header_top, report_header)

                # --- Kolonneheader ---
                header_y = header_top - 22

                # Grå bakgrunn bak kolonneheader (flyttet opp 8 pt)
                canvas.setFillColor(colors.lightgrey)
                canvas.rect(
                    doc.leftMargin,
                    header_y - 4,  # <- dette er nøkkelen
                    sum(col_widths),
                    16,
                    fill=1,
                    stroke=0
                )
                canvas.setFillColor(colors.black)

                # Kolonnenavn (flyttet ned 2 pt)
                canvas.setFont("Helvetica-Bold", 12)
                x = doc.leftMargin
                for i, col in enumerate(visible_columns):
                    canvas.drawString(x + 2, header_y, col)
                    x += col_widths[i]

            doc = SimpleDocTemplate(
                path,
                pagesize=A4,
                leftMargin=16,
                rightMargin=16,
                topMargin=45,  # viktig!
                bottomMargin=16
            )

            story = []
            story.append(Spacer(1, 12))

            # Gruppér rader etter group_col
            groups = {}
            for row in rows:
                key = row[group_col]
                groups.setdefault(key, []).append(row)

            for group_name, group_rows in groups.items():

                # Gruppeheader
                story.append(Paragraph(f"<b>{group_name}</b>", styles["Heading2"]))
                story.append(Spacer(1, 4))

                # Bygg tabellrader uten group_col
                data = []
                for r in group_rows:
                    row_data = [str(x) for i, x in enumerate(r) if i != group_col]
                    data.append(row_data)

                table = Table(data, colWidths=col_widths)

                table.setStyle(TableStyle([
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 12),

                    # Høyrejustering av første og siste kolonne
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (-1, 0), (-1, -1), "LEFT"),

                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]))

                story.append(table)
                story.append(Spacer(1, 14))

            doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)

        except Exception as e:
            logging.error(e)
            msg.error(f"Fikk ikke lagret filen ({path}). Sannsynligvis er forrige versjon åpen og derved låst.")
            return

        os.startfile(path)
        msg.success(f"Fil lastet ned: {path}!")
