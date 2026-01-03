import logging
from datetime import datetime
import pymysql

def delete_inv_customers(conn_mgr, country_code):
    logging.debug("sql.delete_inv_customers")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
        DELETE FROM svr_invoice_customers cust
        WHERE cust.country_code = %s
        """
        cursor.execute(sql, (country_code,))
        conn.commit()
        conn.close()
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def insert_inv_customer(conn_mgr, org: dict):
    logging.debug("sql.insert_inv_customer")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
        INSERT INTO svr_invoice_customers (
            org_id,
            name,
            short_name,
            country_code,
            adr_care_of,
            adr_street,
            adr_city,
            adr_zip_code,
            adr_country,
            mail_adr,
            phone_number,
            mobile_phone_number,
            modified
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
"""
        values = (
            org["org_id"],
            org["name"],
            org["short_name"],
            org["country_code"],
            org["adr_care_of"],
            org["adr_street"],
            org["adr_city"],
            org["adr_zip_code"],
            org["adr_country"],
            org["mail_adr"],
            org["phone_number"],
            org["mobile_phone_number"],
            org["modified"],
        )
        cursor.execute(sql, values)
        conn.commit()
        conn.close()
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def cre_order_bundle(conn_mgr, order_date, remark, currency):
    logging.info("sql.cre_order_bundle")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        sql = """
            INSERT INTO svr_invoice_bundles (
                order_date,
                remark,
                currency,
                invoiced,
                changed
            ) VALUES (%s, %s, %s, 0, %s)
            """
        cursor.execute(sql, (order_date, remark, currency, now,))
        conn.commit()
        conn.close()
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def cre_orders(conn_mgr, bundle_id, raceid):
    logging.info("sql.cre_orders")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        sql = """
            INSERT INTO svr_invoice_orders (
                bundle_id,
                org_id,
                org_name,
                org_adr_l1,
                org_adr_l2,
                org_adr_zip,
                org_adr_city,
                org_adr_country,
                org_mail_adr,
                org_phone_number,
                adr_care_of,
                changed
            )
            with clubs as (
            select distinct n.club
            from names n
            join races r on r.id = n.raceid
            join invoicelevels invlev on invlev.raceid = r.id and invlev.bitmask = (n.invoicelevel & invlev.bitmask)
            where r.id = %s
               and not exists(select org_id from svr_invoice_orders where bundle_id = %s and org_name = n.club)
            )
            select %s
               , cust.org_id
               , clubs.club
               , cust.adr_care_of
               , cust.adr_street
               , cust.adr_zip_code
               , cust.adr_city
               , cust.adr_country
               , cust.mail_adr
               , COALESCE(cust.mobile_phone_number, cust.phone_number) phone
               , cust.adr_care_of
               , now()
            from clubs
            left join svr_invoice_customers cust on cust.name = clubs.club
            """
        cursor.execute(sql, (raceid, bundle_id, bundle_id,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def cre_order_lines(conn_mgr, bundle_id, raceid):
    logging.info("sql.cre_order_lines")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        sql = """
            insert into svr_invoice_order_lines (
                order_id,
                raceid,
                runnerid,
                bitmask,
                changed
            )
            with basis as (
            select n.club, r.id raceid, n.id runnerid, invlev.bitmask, now() changed
            from names n
            join races r on r.id = n.raceid
            join invoicelevels invlev on invlev.raceid = r.id and invlev.bitmask = (n.invoicelevel & invlev.bitmask)
            where r.id = %s
            )
            select ord.order_id, basis.raceid, basis.runnerid, basis.bitmask, basis.changed
            from basis
            join svr_invoice_orders ord on ord.bundle_id = %s and ord.org_name = basis.club
            """
        cursor.execute(sql, (raceid, bundle_id,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def append_remark(conn_mgr, bundle_id, raceid):
    logging.info("sql.append_remark")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        sql = """
        UPDATE svr_invoice_bundles
        SET remark = CONCAT(
            remark,
            (SELECT CONCAT(racedate, ' ', name, '\n')
             FROM races
             WHERE id = %s)
        )
        WHERE id = %s
        """
        cursor.execute(sql, (raceid, bundle_id,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def remove_race_from_remark(conn_mgr, bundle_id, raceid):
    logging.info("sql.remove_race_from_remark")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        sql = """
        UPDATE svr_invoice_bundles b
        SET b.remark = 
            REPLACE(b.remark
            , (SELECT CONCAT(racedate, ' ', name, '\n') FROM races WHERE id = %s)
            , "")
        WHERE id = %s
        """
        cursor.execute(sql, (raceid, bundle_id,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def remove_bundle_from_race(conn_mgr, bundle_id):
    logging.info("sql.remove_race_from_remark")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        sql = """
        UPDATE races r
        SET r.svr_bundle_id = null
        WHERE r.svr_bundle_id = %s
        """
        cursor.execute(sql, (bundle_id,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise



def rem_order_lines(conn_mgr, bundle_id, raceid):
    logging.info("sql.rem_order_lines")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
        delete 
        from svr_invoice_order_lines l
        where l.order_id in (select order_id from svr_invoice_orders o where o.bundle_id = %s)
          and l.raceid = %s
        """
        cursor.execute(sql, (bundle_id, raceid,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def rem_empty_orders(conn_mgr, bundle_id):
    logging.info("sql.rem_empty_orders")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
        delete
        from svr_invoice_orders o
        where o.bundle_id = %s
          and not exists(select id from svr_invoice_order_lines l where l.order_id = o.order_id)
        """
        cursor.execute(sql, (bundle_id,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise


def delete_order_lines(conn_mgr, bundle_id):
    logging.info("sql.delete_order_lines")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
        delete 
        from svr_invoice_order_lines l
        where l.order_id in (select order_id from svr_invoice_orders o where o.bundle_id = %s)
        """
        cursor.execute(sql, (bundle_id,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def delete_orders(conn_mgr, bundle_id):
    logging.info("sql.delete_orders")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
        delete 
        from svr_invoice_orders o
        where o.bundle_id = %s
        """
        cursor.execute(sql, (bundle_id,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def delete_bundle(conn_mgr, bundle_id):
    logging.info("sql.delete_bundle")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
        delete 
        from svr_invoice_bundles b
        where b.id = %s
        """
        cursor.execute(sql, (bundle_id,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise


def export_tripletex(conn_mgr, bundle_id, order_no_base, customer_no_base):
    logging.info("sql.export_tripletex")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = f"""
    select {order_no_base} + o.order_id 'ORDER NO'
        ,b.order_date 'ORDER DATE'
        ,{customer_no_base} + o.org_id 'CUSTOMER NO'
        ,o.org_name customer_name
        ,o.org_mail_adr customer_email
        ,o.org_phone_number
        ,o.org_adr_l1 'POSTAL ADDR - LINE 1'
        ,o.org_adr_l2 'POSTAL ADDR - LINE 2' 
        ,o.org_adr_zip 'POSTAL ADDR - POSTAL NO'
        ,o.org_adr_city 'POSTAL ADDR - CITY'
        ,o.org_adr_country 'POSTAL ADDR - COUNTRY'
        ,b.remark comments
        ,b.currency currency
        ,b.order_date delivery_date
        ,CONCAT(r.racedate, '    ', cl.name, '   : ', n.name, " (", lev.description, ")") 'ORDER LINE - DESCRIPTION'
        ,lev.price 'ORDER LINE - UNIT PRICE'
        ,1 'ORDER LINE - COUNT'
        ,6 'ORDER LINE - VAT CODE'
    from svr_invoice_order_lines l
    join svr_invoice_orders o on o.order_id = l.order_id
    join svr_invoice_bundles b on b.id = o.bundle_id and b.id = %s
    join names n on n.id = l.runnerid and n.raceid = l.raceid
    join classes cl on cl.id = n.classid
    join races r on r.id = l.raceid
    join invoicelevels lev on lev.raceid = l.raceid and lev.bitmask = l.bitmask
    where COALESCE(o.dont_export, 0) = 0
    order by customer_name, r.racedate, cl.name, n.name, lev.description COLLATE utf8mb3_danish_ci
    """
    try:
        cursor.execute(sql, (bundle_id,))
        return cursor.fetchall(), [desc[0] for desc in cursor.description]
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise



def select_bundles(conn_mgr):
    logging.info("sql.select_bundles")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = """
    select
        id Bunt_ID,
        order_date Fakturadato,
        remark Beskrivelse,
        currency Valuta,
        invoiced Fakturert,
        changed Opprettet
    from svr_invoice_bundles
    order by id desc
    """
    try:
        cursor.execute(sql)
        return cursor.fetchall(), [desc[0] for desc in cursor.description]
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def select_orders(conn_mgr, bundle_id, order_no_base, customer_no_base):
    logging.info("sql.select_orders")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = f"""
    select 
        order_id OrderID,
        {order_no_base} + order_id Ordrenr,
        bundle_id,
        org_id OrgID,
        {customer_no_base} + org_id Kundenr,
        org_name Klubb,
        org_adr_l1 Adresse1,
        org_adr_l2 Adresse2,
        org_adr_zip Postnr,
        org_adr_city Sted,
        org_adr_country Land,
        org_mail_adr Epost,
        org_phone_number Tlf,
        COALESCE(dont_export, 0) 'Eksport',
        changed Endret
    from svr_invoice_orders
    where bundle_id = %s
    order by org_name COLLATE utf8mb3_danish_ci 
    """
    try:
        cursor.execute(sql, (bundle_id,))
        return cursor.fetchall(), [desc[0] for desc in cursor.description]
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def select_norge_orders(conn_mgr, bundle_id):
    logging.info("sql.select_orders")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = """
    select 
        order_id,
        bundle_id,
        org_id,
        org_name,
        org_adr_country
    from svr_invoice_orders
    where bundle_id = %s
      and org_adr_country = 'Norge'
    order by org_name COLLATE utf8mb3_danish_ci
    """
    try:
        cursor.execute(sql, (bundle_id,))
        return cursor.fetchall(), [desc[0] for desc in cursor.description]
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise


def select_order_lines(conn_mgr, order_id):
    logging.info("sql.select_order_lines")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = """
    select 
        l.id,
        l.order_id Ordrenr,
        l.raceid,
        r.racedate Løpsdato,
        r.name Løp,
        cl.name Klasse,
        l.runnerid,
        n.name Løper,
        l.bitmask,
        invlev.name Priskode,
        invlev.description Produkt,
        invlev.price Pris,
        l.changed Endret
    from svr_invoice_order_lines l
    join races r on r.id = l.raceid
    join names n on n.id = l.runnerid
    join classes cl on cl.id = n.classid and cl.cource = 0
    join invoicelevels invlev on invlev.raceid = l.raceid and invlev.bitmask = l.bitmask
    where order_id = %s
    order by r.racedate, r.name, cl.name, n.name, l.bitmask COLLATE utf8mb3_danish_ci
    """
    try:
        cursor.execute(sql, (order_id,))
        return cursor.fetchall(), [desc[0] for desc in cursor.description]
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def select_order(conn_mgr, order_id, order_no_base):
    logging.info("sql.select_order")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = f"""
    select 
        o.org_name Klubb, 
        o.order_id OrderID,
        {order_no_base} + o.order_id Ordrenummer,
        b.order_date Ordredato,
        b.remark Beskrivelse,
        concat(o.org_adr_l1, ", ", o.org_adr_l2, ", ", o.org_adr_zip, " ", o.org_adr_city, ", ", o.org_adr_country) Adresse,
        o.org_mail_adr E_post,
        o.org_phone_number Telefonnr,
        CONCAT(r.racedate, '    ', cl.name, '   : ', n.name, " (", invlev.description, ")") Ordrelinje,
        invlev.price Beløp,
        b.currency Valuta,
        invlev.name Priskode,
        invlev.description Produkt
    from svr_invoice_order_lines l
    join svr_invoice_orders o on o.order_id = l.order_id
    join svr_invoice_bundles b on b.id = o.bundle_id
    join races r on r.id = l.raceid
    join names n on n.id = l.runnerid
    join classes cl on cl.id = n.classid and cl.cource = 0
    join invoicelevels invlev on invlev.raceid = l.raceid and invlev.bitmask = l.bitmask
    where o.order_id = %s
    order by r.racedate, r.name, cl.name, n.name, invlev.name COLLATE utf8mb3_danish_ci
    """
    try:
        cursor.execute(sql, (order_id,))
        return cursor.fetchall(), [desc[0] for desc in cursor.description]
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise


def read_race_list(conn_mgr):
    logging.info("db.read_race_list")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = """
    SELECT r.racedate Dag, r.name Løp, r.svr_bundle_id Bunt_ID, r.id
    FROM races r
    ORDER BY r.racedate DESC, r.created COLLATE utf8mb3_danish_ci DESC
    """
    cursor.execute(sql)
    return cursor.fetchall(), [desc[0] for desc in cursor.description]

#
# Sjekk om database objektene til Trekkeplan er installert.
#
def is_db_objects_installed(conn_mgr):
    logging.info("sql.is_db_objects_installed")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
        SHOW COLUMNS FROM races LIKE 'svr_bundle_id'
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        row_count = len(rows)
        return row_count > 0
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def is_db_at_least_version_8(conn_mgr):
    logging.info("sql.is_db_objects_installed")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
        select version()
        """
        cursor.execute(sql)
        version = cursor.fetchone()[0]  # f.eks. '8.0.36'

        major, minor, *_ = version.split('.')
        major = int(major)
        minor = int(minor)

        if major < 8:
            raise RuntimeError(
                f"MySQL {version} oppdaget. "
                "Denne modulen krever MySQL 8.0 eller nyere, ref. README.pdf."
            )
        return version
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise


def install_db_objects(conn_mgr):
    logging.info("sql.install_db_objects")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = "ALTER TABLE races ADD COLUMN svr_bundle_id int"
        cursor.execute(sql)
        sql = """
        CREATE TABLE `svr_invoice_customers` (
            org_id INT NOT NULL,
            `name` VARCHAR(100) NOT NULL,
            short_name VARCHAR(100),
            country_code VARCHAR(100),
            adr_care_of VARCHAR(100),
            adr_street VARCHAR(100),
            adr_zip_code VARCHAR(100),
            adr_city VARCHAR(100),
            adr_country VARCHAR(100),
            mail_adr VARCHAR(100),
            phone_number VARCHAR(100),
            mobile_phone_number VARCHAR(100),
            modified datetime,
            PRIMARY KEY (org_id),
            INDEX contry_code_i1 (country_code ASC)
        )
        """
        cursor.execute(sql)
        sql = """
        CREATE TABLE svr_invoice_bundles (
            id INT NOT NULL AUTO_INCREMENT,
            order_date date not null,
            remark VARCHAR(1000) not null,
            currency VARCHAR(30),
            invoiced INT, -- 1 = TRUE
            changed DATETIME NOT NULL,
            PRIMARY KEY (id)
        )  AUTO_INCREMENT=1
        """
        cursor.execute(sql)
        sql = """
        CREATE TABLE svr_invoice_orders (
            order_id INT NOT NULL AUTO_INCREMENT,
            bundle_id int not null,
            org_id int,
            org_name VARCHAR(100),
            org_adr_l1 VARCHAR(200),
            org_adr_l2 VARCHAR(200),
            org_adr_zip VARCHAR(200),
            org_adr_city VARCHAR(200),
            org_adr_country VARCHAR(200),
            org_mail_adr VARCHAR(100),
            org_phone_number VARCHAR(100),
            adr_care_of VARCHAR(100),
            org_no VARCHAR(20),
            dont_export int,
            changed DATETIME NOT NULL,
            PRIMARY KEY (order_id),
            INDEX inv_order_i1 (bundle_id)
        )  AUTO_INCREMENT=1000
        """
        cursor.execute(sql)
        sql = """
        CREATE TABLE svr_invoice_order_lines (
            id INT NOT NULL AUTO_INCREMENT,
            order_id INT NOT NULL,
            raceid INT NOT NULL,
            runnerid INT NOT NULL,
            bitmask SMALLINT unsigned NOT NULL,
            changed DATETIME NOT NULL,
            PRIMARY KEY (id),
            UNIQUE INDEX inv_line_ui1 (order_id, raceid, runnerid, bitmask)
        )  AUTO_INCREMENT=1
        """
        cursor.execute(sql)
        logging.info("Database objects installed!")

    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def upd_race_bundle_id(conn_mgr, raceid, new_value):
    logging.info("sql.upd_race_bundle_id, raceid: %s", raceid)
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
        UPDATE races
        set svr_bundle_id = %s
        WHERE id = %s
        """
        cursor.execute(sql, (new_value, raceid))
        conn.commit()
        conn.close()
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def upd_org_no(conn_mgr, order_id, org_no):
#    logging.info("sql.upd_org_no, org_id: %s", order_id)
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
        UPDATE svr_invoice_orders
        set org_no = %s
        WHERE order_id = %s
        """
        cursor.execute(sql, (org_no, order_id))
        conn.commit()
        conn.close()
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def toggle_dont_export(conn_mgr, order_id):
    logging.info("sql.upd_dont_export")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
        UPDATE svr_invoice_orders
        set dont_export = 1-COALESCE(dont_export, 0)
        WHERE order_id = %s
        """
        cursor.execute(sql, (order_id,))
        conn.commit()
        conn.close()
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def make_amount_per_club(conn_mgr, bundle_id, order_no_base, customer_no_base):
    logging.info("sql.make_amount_per_club")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = f"""
    select 
         min({order_no_base} + o.order_id) Ordrenr
        ,o.org_name Klubb
        ,sum(lev.price) Beløp
    from svr_invoice_order_lines l
    join svr_invoice_orders o on o.order_id = l.order_id
    join svr_invoice_bundles b on b.id = o.bundle_id and b.id = %s
    join names n on n.id = l.runnerid and n.raceid = l.raceid
    join classes cl on cl.id = n.classid
    join races r on r.id = l.raceid
    join invoicelevels lev on lev.raceid = l.raceid and lev.bitmask = l.bitmask
	group by o.org_name
    order by o.org_name COLLATE utf8mb3_danish_ci
    """
    try:
        cursor.execute(sql, (bundle_id,))
        return cursor.fetchall(), [desc[0] for desc in cursor.description]
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def make_amount_per_club_product(conn_mgr, bundle_id, order_no_base, customer_no_base):
    logging.info("sql.make_amount_per_club_product")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = f"""
    select 
         min({order_no_base} + o.order_id) Ordrenr
        ,o.org_name Klubb
        ,lev.description
        ,sum(lev.price) Beløp
    from svr_invoice_order_lines l
    join svr_invoice_orders o on o.order_id = l.order_id
    join svr_invoice_bundles b on b.id = o.bundle_id and b.id = %s
    join names n on n.id = l.runnerid and n.raceid = l.raceid
    join classes cl on cl.id = n.classid
    join races r on r.id = l.raceid
    join invoicelevels lev on lev.raceid = l.raceid and lev.bitmask = l.bitmask
	group by o.org_name, lev.description
    order by o.org_name COLLATE utf8mb3_danish_ci, lev.description COLLATE utf8mb3_danish_ci
    """
    try:
        cursor.execute(sql, (bundle_id,))
        return cursor.fetchall(), [desc[0] for desc in cursor.description]
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def make_amount_per_product(conn_mgr, bundle_id, order_no_base, customer_no_base):
    logging.info("sql.make_amount_per_club")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = f"""
    select 
         lev.description Produkt
        ,sum(lev.price) Beløp
    from svr_invoice_order_lines l
    join svr_invoice_orders o on o.order_id = l.order_id
    join svr_invoice_bundles b on b.id = o.bundle_id and b.id = %s
    join names n on n.id = l.runnerid and n.raceid = l.raceid
    join classes cl on cl.id = n.classid
    join races r on r.id = l.raceid
    join invoicelevels lev on lev.raceid = l.raceid and lev.bitmask = l.bitmask
	group by lev.description
    order by lev.description COLLATE utf8mb3_danish_ci
    """
    try:
        cursor.execute(sql, (bundle_id,))
        return cursor.fetchall(), [desc[0] for desc in cursor.description]
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def make_amount_per_product_club(conn_mgr, bundle_id, order_no_base, customer_no_base):
    logging.info("sql.make_amount_per_product_club")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = f"""
    select 
         min({order_no_base} + o.order_id) Ordrenr
        ,o.org_name Klubb
        ,lev.description
        ,sum(lev.price) Beløp
    from svr_invoice_order_lines l
    join svr_invoice_orders o on o.order_id = l.order_id
    join svr_invoice_bundles b on b.id = o.bundle_id and b.id = %s
    join names n on n.id = l.runnerid and n.raceid = l.raceid
    join classes cl on cl.id = n.classid
    join races r on r.id = l.raceid
    join invoicelevels lev on lev.raceid = l.raceid and lev.bitmask = l.bitmask
	group by lev.description, o.org_name
    order by lev.description COLLATE utf8mb3_danish_ci, o.org_name COLLATE utf8mb3_danish_ci
    """
    try:
        cursor.execute(sql, (bundle_id,))
        return cursor.fetchall(), [desc[0] for desc in cursor.description]
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

def make_amount_per_race_product(conn_mgr, bundle_id):
    logging.info("sql.make_amount_per_club")
    conn = conn_mgr.get_connection()
    cursor = conn.cursor()
    sql = f"""
    select 
         r.name Løp
		,lev.description Produkt
        ,min(lev.price) Pris
        ,count(l.id) Antall
        ,sum(lev.price) Beløp
    from svr_invoice_order_lines l
    join svr_invoice_orders o on o.order_id = l.order_id
    join svr_invoice_bundles b on b.id = o.bundle_id and b.id = %s
    join names n on n.id = l.runnerid and n.raceid = l.raceid
    join classes cl on cl.id = n.classid
    join races r on r.id = l.raceid
    join invoicelevels lev on lev.raceid = l.raceid and lev.bitmask = l.bitmask
	group by r.name, lev.description
    order by r.name COLLATE utf8mb3_danish_ci, lev.description COLLATE utf8mb3_danish_ci
    """
    try:
        cursor.execute(sql, (bundle_id,))
        return cursor.fetchall(), [desc[0] for desc in cursor.description]
    except pymysql.Error as err:
        logging.error(f"MySQL-feil: {err}")
        raise
    except Exception as e:
        logging.error(f"Uventet feil: {e}")
        raise

