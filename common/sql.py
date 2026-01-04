import logging


def read_race_list(conn_mgr):
    logging.info("db.read_race_list")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = """
    SELECT r.id Løps_Id, r.racedate Dag, r.name Løp, time(r.svr_first_start) Starttid, r.svr_bundle_id Bunt_ID
    FROM races r
    ORDER BY r.racedate DESC, r.created COLLATE utf8mb3_danish_ci DESC
    """
    cursor.execute(sql)
    return cursor.fetchall(), [desc[0] for desc in cursor.description]

