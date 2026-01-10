import datetime
import logging
from decimal import Decimal
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# from fakturagrunnlag.db import sql
from common.connection import ConnectionManager
from direkteresultater.db import sql
from direkteresultater.server.server_control import ServerControl


class InfoHandler(BaseHTTPRequestHandler):
    #        conn_mgr: ConnectionManager = None

    def do_GET(self):
        parsed = urlparse(self.path)

        server_control = self.server.server_control
        server_control.request_count += 1
        server_control.parent.request_count_label.setText(
            f"Forespørsler mottatt: {server_control.request_count}"
        )
        server_control.parent.last_request_label.setText(
            f"Siste forespørsel: {self.path} kl. {datetime.datetime.now().strftime('%H:%M:%S')}"
        )



        if parsed.path == "/infoskjerm":
            params = parse_qs(parsed.query)
            race = int(params.get("race", [0])[0])
            cl_from = int(params.get("cl_from", [1])[0])
            cl_to = int(params.get("cl_to", [999])[0])
            scroll = int(params.get("scroll", [5])[0])
            step_px = int(params.get("px", [1])[0])

            pause = 2500 # min(max(20 / scroll, 1),8)*1000
            logging.info(f"pause (ms) = {pause}")

            rows, columns = sql.make_result(InfoHandler.conn_mgr, race, cl_from, cl_to)
            html = result_html_table(rows, columns, 1, "strong", 1)

            if len(rows) > 0:
                race_name = rows[0][0]
            else:
                race_name = "Løp"

            full_html = f"""
<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<title>{race_name}</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background: #f7f7f7;
    color: #222;
    margin: 0;
    padding: 0;
}}
table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
}}
tr.gruppe {{
    position: sticky;
    top: 0;
    background: #e0e0e0;      /* eller en annen bakgrunnsfarge */
    color: #000;
    z-index: 10;           /* slik at den ligger over data-rader */
    font-weight: bold;
    border-bottom: 2px solid #999;
}}
td, th {{
    padding: 6px 10px;
    border-bottom: 1px solid #333;
}}
td.num {{
    text-align: right;
    white-space: nowrap;
}}
</style>

</head>
<body>
{html}
<script>
history.scrollRestoration = "manual";

let speed = {scroll};
let pos = 0;
let lastY = -1;
let active = false;

function scrollStep() {{
    if (!active) return;

    // Alltid 1 px per steg
    pos += {step_px}; // default 1
    window.scrollTo(0, pos);

    if (window.scrollY === lastY) {{
        active = false;
        setTimeout(() => {{
            sessionStorage.setItem("afterReload", "yes");
            location.reload();
        }}, {pause});
        return;
    }}

    lastY = window.scrollY;

    const maxDelay = 20;   // speed = 1
    const minDelay = 4;    // speed = 10
    const delay = maxDelay - (speed - 1) * (maxDelay - minDelay) / 9;

    setTimeout(() => requestAnimationFrame(scrollStep), delay);
}}

function startScrolling() {{
    pos = 0;
    lastY = -1;
    window.scrollTo(0, 0);
    active = true;
    requestAnimationFrame(scrollStep);
}}

window.onload = function() {{
    if (sessionStorage.getItem("afterReload") === "yes") {{
        sessionStorage.removeItem("afterReload");
        setTimeout(startScrolling, 2*{pause});
    }} else {{
        setTimeout(startScrolling, 2*{pause});
    }}
}};
</script>
</body>
</html>
"""

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(full_html.encode("utf-8"))
            return

        self.send_error(404, "Not Found")

def result_html_table(rows, columns, group_by_index: int, heading_tag="strong", border=1):
    grupper = {}
    visningsindekser = [2,3,4,5,6,7,8]
    html = f"<table border='{border}'>\n"
    for row in rows:
        nøkkel = row[group_by_index]

        if nøkkel not in grupper:
            grupper[nøkkel] = []
            # legg inn overskrift som egen rad
            html += (
                f"  <tr class='gruppe'><td colspan='{len(visningsindekser)}'>"
                f"<{heading_tag}>{nøkkel}</{heading_tag}></td></tr>\n"
            )

        grupper[nøkkel].append(row)

        # bygg dataraden
        celler = []
        # Plassering
        verdi = row[2]
        if not verdi:
            verdi = "-"
        celler.append(f"<td class='num'>{verdi}</td>")

        # Navn
        verdi = row[3]
        celler.append(f"<td>{verdi}</td>")

        # Klubb
        verdi = row[4]
        celler.append(f"<td>{verdi}</td>")

        # Starttid
#        verdi = row[5]
#        celler.append(f"<td>{verdi}</td>")

        # Ekstrainfo
        status = row[8]
        diff2 = row[9] # Diff hvis ikke i mål ennå.
        dagersiden = row[10] # Dager siden løpet. Diff2 brukes kun på løpsdagen.

        # Tid
        verdi = row[6]
        if status == "OK":
            verdi = format_mysql_time(verdi)
        else:
            verdi = status
        celler.append(f"<td class='num'>{verdi}</td>")

        #Diff
        if status == "OK":
            verdi = row[7]
            verdi = "+"+format_mysql_time(verdi)
        elif dagersiden == 0:
            verdi = diff2
        else:
            verdi = ""
        celler.append(f"<td class='num'>{verdi}</td>")

        html += "  <tr>" + "".join(celler) + "</tr>\n"
    html += "</table>"
    return html

def format_cell(value):
    # Tall med tusenskilletegn (norsk stil)
    if isinstance(value, int):
        return f"{value:,}".replace(",", " ")
    if isinstance(value, float) or isinstance(value, Decimal):
        s = f"{value:,.2f}".replace(",", " ")
        return s.replace(".", ",")
    return value

def format_mysql_time(td:datetime.timedelta):
    if td is None:
        return ""
    total_seconds = td.seconds  # timedelta -> sekunder (0–86399)

    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60

    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    else:
        return f"{m}:{s:02d}"
