import sqlite3
import MySQLdb

# SQLite connection
sqlite_conn = sqlite3.connect("database.db")
sqlite_cursor = sqlite_conn.cursor()

# MySQL connection
mysql_conn = MySQLdb.connect(
    host="10.161.235.42", user="ets1szh", passwd="estbangbangde", db="zeekr"
)
mysql_cursor = mysql_conn.cursor()

# Retrieve data from SQLite
sqlite_cursor.execute(
    "SELECT soc_version, cus_version, tester, bench_id, test_type, start_time, end_time, error_keyword, result FROM stability"
)
rows = sqlite_cursor.fetchall()

# Insert data into MySQL
insert_query = "INSERT INTO stability (soc_version, cus_version, tester, bench_id, test_type, start_time, end_time, error_keyword, result) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
mysql_cursor.executemany(insert_query, rows)

# Commit changes and close connections
mysql_conn.commit()
mysql_conn.close()
sqlite_conn.close()
