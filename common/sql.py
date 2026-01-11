import logging
import pymysql


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


def is_db_objects_installed(conn_mgr):
    logging.info("sql.is_db_objects_installed")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = """
SHOW COLUMNS FROM races LIKE 'svr_first_start'
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


def install_db_objects(conn_mgr):
    logging.info("sql.install_db_objects")
    try:
        conn = conn_mgr.get_connection()
        cursor = conn.cursor()
        sql = "ALTER TABLE races ADD COLUMN svr_first_start DATETIME"
        cursor.execute(sql)
        sql = "ALTER TABLE races ADD COLUMN svr_draw_time DATETIME"
        cursor.execute(sql)
        sql = "ALTER TABLE races ADD COLUMN svr_drawplan_changed DATETIME"
        cursor.execute(sql)
        sql = "ALTER TABLE races ADD COLUMN svr_bundle_id int"
        cursor.execute(sql)
        sql = """
CREATE TABLE `svr_startblocks` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`raceid` INT NOT NULL,
	`name` VARCHAR(80) NOT NULL DEFAULT '',
	PRIMARY KEY (`id`),
	UNIQUE INDEX `name` (`name` ASC, `raceid` ASC)
)
AUTO_INCREMENT=1
"""
        cursor.execute(sql)
        sql = """
CREATE TABLE `svr_startblocklags` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`startblockid` INT NULL DEFAULT NULL,
	`timelag` INT NULL DEFAULT NULL,
	`timegap` INT NULL DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE INDEX `startblockid_lag` (`startblockid`, `timelag`)
)
AUTO_INCREMENT=1
    """
        cursor.execute(sql)
        sql = """
 CREATE TABLE `svr_classstarts` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`blocklagid` INT NOT NULL,
	`classid` INT NOT NULL,
	`timegap` INT NULL DEFAULT NULL,
	`freebefore` INT NULL DEFAULT NULL,
	`freeafter` INT NULL DEFAULT NULL,
	`sortorder` INT NOT NULL,
	`qtybefore` INT NULL DEFAULT NULL,
	`classstarttime` DATETIME NULL DEFAULT NULL,
	`nexttime` DATETIME NULL DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE INDEX `classid` (`classid`)
)
AUTO_INCREMENT=1
"""
        cursor.execute(sql)
        sql = """
CREATE TABLE `svr_classstarts_not` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`classid` INT NOT NULL,
	PRIMARY KEY (`id`),
	UNIQUE INDEX `classid` (`classid`)
)
AUTO_INCREMENT=1
"""
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


def read_race(conn_mgr, raceid):
    logging.info("read_race: %s", raceid)
    conn = conn_mgr.get_connection()

    cursor = conn.cursor()
    sql = """
SELECT r.id, r.name, r.racedate, r.svr_first_start, r.svr_drawplan_changed, r.svr_draw_time
FROM races r 
WHERE r.id = %s
"""
    cursor.execute(sql, (raceid,))
    return cursor.fetchall(), [desc[0] for desc in cursor.description]
