import pygsheets
import sqlite3
import pprint


def push():
    gc = pygsheets.authorize(client_secret='/home/users/jeffderb/.client_secret.json')
    sh = gc.open_by_key('1Ij-ci1RjQG-w7Qhy1wMITZNi_KAbJz7q_RMf_ju9XS4')
    wks = sh.sheet1
    conn = sqlite3.connect('/home/users/jeffderb/db/migration.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT a.server, b.volume, c.log_file, c.date, d.snippet, d.message "
                   "FROM servers a, volumes b "
                   "INNER JOIN log_files c ON c.server_id = a.rowid AND c.volume_id = b.rowid "
                   "INNER JOIN log_file_detail d ON d.log_file_id = c.rowid "
                   "GROUP BY a.server, b.volume "
                   "ORDER BY a.server, b.volume ")
    results = cursor.fetchall()
    pprint.pprint(results)
    # wks.update_values('A2', results)
    return 'report sent to gsheets'


if __name__ == '__main__':
    push()
