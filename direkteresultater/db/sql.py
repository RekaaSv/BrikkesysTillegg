import logging
import pymysql

def make_result(conn_mgr, race_id, order_from, order_to):
    logging.info("sql.make_result")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = """
with all_classes as
(select cl.id, cl.name, row_number() over (order by cl.sortorder) radnr
from classes cl
where cl.raceid = %s
)
select r.name Løp, c.name Klasse
	,cast(if(n.status = 'A', RANK() OVER (PARTITION BY n.classid ORDER BY s.statuscode, n.time), null) as unsigned)  Plass
    , n.name Navn, n.club Klubb
    ,time(n.starttime) Start
    ,n.time Tid
    ,timediff(n.time, min(n.time) OVER (PARTITION BY n.classid ORDER BY s.statuscode, n.time)) Diff
    ,s.statustext Status
    ,timediff(timediff(time(now()), time(n.starttime)), min(n.time) OVER (PARTITION BY n.classid ORDER BY s.statuscode, n.time)) Diff2 
    ,datediff(date(now()), date(n.starttime)) Dagersiden
from names n
join all_classes c on c.id = n.classid
join races r on r.id = n.raceid
JOIN status s on s.statuscode = n.status
where r.id = %s
  and c.radnr between %s and %s
order by c.radnr, s.statuscode, n.time, n.starttime
    """
    try:
        cursor.execute(sql, (race_id, race_id, order_from, order_to))
        return cursor.fetchall(), [desc[0] for desc in cursor.description]
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise


