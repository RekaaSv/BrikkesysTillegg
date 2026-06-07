from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import KeepTogether
from reportlab.pdfbase.pdfmetrics import stringWidth
import os
import logging


class PdfBuilder:

    @staticmethod
    def get_download_path(fie_name):
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        return os.path.join(downloads_path, fie_name)

    # --- Truncation-funksjon basert på faktisk tekstbredde ---
    @staticmethod
    def truncate_to_width(text, max_width, font="Helvetica", size=12):
        text = str(text)
        if stringWidth(text, font, size) <= max_width:
            return text

        ellipsis = "…"
        ellipsis_width = stringWidth(ellipsis, font, size)

        # Kutt ned til det passer
        for i in range(len(text), 0, -1):
            candidate = text[:i]
            if stringWidth(candidate, font, size) + ellipsis_width <= max_width:
                return candidate + ellipsis

        return ellipsis

    @staticmethod
    def build_startlist_pdf(msg, rows, columns, group_col, report_header, file_name):
        path = PdfBuilder.get_download_path(file_name)

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

                # --- Rapportnavn (på alle sider) ---
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

    @staticmethod
    def build_starterlist_pdf(msg, rows, columns, group_col, report_header, file_name):

        path = PdfBuilder.get_download_path(file_name)

        try:
            styles = getSampleStyleSheet()

            # Kolonne 5 (Starttid) er gruppeheader → tabellen har 6 kolonner
            visible_columns = [col for i, col in enumerate(columns) if i != group_col]

            # Bredder som passer A4 perfekt
            col_widths = [40, 160, 160, 60, 80, 63]

            # Header-funksjon
            def draw_header(canvas, doc):
                page_width, page_height = canvas._pagesize
                header_top = page_height - 20

                # --- Rapportnavn (på alle sider) ---
                canvas.setFont("Helvetica-Bold", 16)
                canvas.drawString(doc.leftMargin, header_top, report_header)

                # Kolonneheader
                header_y = header_top - 22

                # Grå stripe
                canvas.setFillColor(colors.lightgrey)
                canvas.rect(
                    doc.leftMargin,
                    header_y - 4,
                    sum(col_widths),
                    16,
                    fill=1,
                    stroke=0
                )
                canvas.setFillColor(colors.black)

                # Kolonnenavn
                canvas.setFont("Helvetica-Bold", 12)
                x = doc.leftMargin
                for i, col in enumerate(visible_columns):
                    canvas.drawString(x + 2, header_y, col)
                    x += col_widths[i]

            # Dokument
            doc = SimpleDocTemplate(
                path,
                pagesize=A4,
                leftMargin=16,
                rightMargin=16,
                topMargin=70,
                bottomMargin=16
            )

            story = []
            story.append(Spacer(1, 12))

            # Gruppér rader etter Starttid
            groups = {}
            for row in rows:
                key = row[group_col]
                groups.setdefault(key, []).append(row)

            for group_value, group_rows in groups.items():

                # --- Bygg gruppeblokk som skal holdes samlet ---
                group_block = []

                # Gruppeheader (Starttid)
                group_block.append(Paragraph(
                    f"<para alignment='right'><b>{group_value}</b></para>",
                    styles["Heading3"]
                ))
                group_block.append(Spacer(1, 2))

                # Bygg tabellrader uten group_col
                data = []
                for r in group_rows:
                    visible_values = [x for j, x in enumerate(r) if j != group_col]

                    row_data = []
                    for i, x in enumerate(visible_values):
                        cell = str(x)

                        # Trunkering av Klubb-kolonnen (kolonne 2 etter fjerning av group_col)
                        if i in [1, 2]:
                            cell = PdfBuilder.truncate_to_width(cell, 156)  # 160 - padding

                        row_data.append(cell)

                    data.append(row_data)

                table = Table(data, colWidths=col_widths)
                table.hAlign = "LEFT"

                table.setStyle(TableStyle([
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 12),

                    # Justeringer
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),   # Startnr
                    ("ALIGN", (3, 0), (3, -1), "LEFT"),    # Brikke
                    ("ALIGN", (5, 0), (5, -1), "LEFT"),    # Startet

                    # Padding
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]))

                group_block.append(table)
                group_block.append(Spacer(1, 4))

                # --- Hele gruppen skal holdes samlet ---
                story.append(KeepTogether(group_block))

            doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)

        except Exception as e:
            logging.error(e)
            msg.error(f"Fikk ikke lagret filen ({path}). Sannsynligvis er forrige versjon åpen og derved låst.")
            return

        os.startfile(path)
        msg.success(f"Fil lastet ned: {path}!")

    @staticmethod
    def build_clublist_pdf(msg, rows, columns, group_col, report_header, file_name):
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        import logging, os

        styles = getSampleStyleSheet()

        # Fjern group_col fra kolonneoverskriftene
        visible_columns = [col for i, col in enumerate(columns) if i != group_col]

        # Kolonnebredder for Klasse, Startnr, Navn, Brikke, Starttid
        col_widths = [80, 50, 180, 70, 70]

        # Header-funksjon
        def draw_header(canvas, doc):
            page_width, page_height = canvas._pagesize
            header_top = page_height - 20

            # --- Rapportnavn (på alle sider) ---
            canvas.setFont("Helvetica-Bold", 16)
            canvas.drawString(doc.leftMargin, header_top, report_header)

            # Kolonneheader
            header_y = header_top - 22

            # Grå stripe
            canvas.setFillColor(colors.lightgrey)
            canvas.rect(
                doc.leftMargin,
                header_y - 4,
                sum(col_widths),
                16,
                fill=1,
                stroke=0
            )
            canvas.setFillColor(colors.black)

            # Kolonnenavn (uten group_col)
            canvas.setFont("Helvetica-Bold", 12)
            x = doc.leftMargin
            for i, col in enumerate(visible_columns):
                canvas.drawString(x + 2, header_y, col)
                x += col_widths[i]

        # Dokument
        path = PdfBuilder.get_download_path(file_name)
        doc = SimpleDocTemplate(
            path,
            pagesize=A4,
            leftMargin=16,
            rightMargin=16,
            topMargin=70,
            bottomMargin=16
        )

        story = []

        # Gruppér rader etter group_col
        groups = {}
        for row in rows:
            key = row[group_col]
            groups.setdefault(key, []).append(row)

        # Sorter gruppene alfabetisk
        sorted_groups = sorted(groups.keys())

        first = True
        for group_value in sorted_groups:
            group_rows = groups[group_value]

            # Ny side for hver klubb (unntatt første)
            if not first:
                story.append(PageBreak())
            first = False

            # Gruppeheader (klubbnavn) – ingen truncering
            story.append(Paragraph(
                f"<para alignment='left'><b>{group_value}</b></para>",
                styles["Heading3"]
            ))
            story.append(Spacer(1, 4))

            # Bygg tabellrader uten group_col
            data = []
            for r in group_rows:
                visible_values = [x for i, x in enumerate(r) if i != group_col]

                row_data = []
                for i, x in enumerate(visible_values):
                    cell = str(x)

                    # Truncering på Navn (kolonne 2 etter fjerning av group_col)
                    if i == 2:
                        cell = PdfBuilder.truncate_to_width(cell, 170)

                    row_data.append(cell)

                data.append(row_data)

            table = Table(data, colWidths=col_widths)
            table.hAlign = "LEFT"

            table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),

                ("ALIGN", (1, 0), (1, -1), "RIGHT"),  # Startnr
                ("ALIGN", (3, 0), (3, -1), "LEFT"),   # Brikke
                ("ALIGN", (4, 0), (4, -1), "LEFT"),   # Starttid

                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))

            story.append(table)
            story.append(Spacer(1, 6))

        # Bygg PDF
        try:
            doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)
        except Exception as e:
            logging.error(e)
            msg.error(f"Fikk ikke lagret filen ({path}). Sannsynligvis er forrige versjon åpen og derved låst.")
            return

        os.startfile(path)
        msg.success(f"Fil lastet ned: {path}!")
