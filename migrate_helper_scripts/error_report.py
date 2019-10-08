import pygsheets
import sqlite3
import pprint


def push():
    gc = pygsheets.authorize(client_secret='/home/users/jeffderb/.client_secret.json')
    sh = gc.open_by_key('1Ij-ci1RjQG-w7Qhy1wMITZNi_KAbJz7q_RMf_ju9XS4')
    wks = sh.sheet1
    conn = sqlite3.connect('db/migration.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT a.server, b.volume, c.log_file, d.message, c.date, d.snippet "
                   "FROM servers a, volumes b "
                   "INNER JOIN log_files c ON c.server_id = a.rowid AND c.volume_id = b.rowid "
                   "INNER JOIN log_file_detail d ON d.log_file_id = c.rowid "
                   "ORDER BY a.server, b.volume ")
    results = cursor.fetchall()
    # report_file = open('/home/users/jeffderb/db/error_report.csv', 'w')
    #for row in results:
    #    report_file.write("|".join(row) + "\n")
    #report_file.close()
    # pprint.pprint(results)
    wks.insert_rows(row=2, number=len(results), values=results)
    # wks.update_values('A2', results)
    return 'report to /home/users/jeffderb/db/error_report'


if __name__ == '__main__':
    push()
