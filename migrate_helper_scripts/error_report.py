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
    wks.clear('A2')
    row_values = {}
    all_values = []

    # report_file = open('/home/users/jeffderb/db/error_report.csv', 'w')
    for row in results:
        row_values['server'] = row[0]
        row_values['volume'] = row[1]
        row_values['log_file'] = row[2]
        row_values['message'] = row[3]
        row_values['date'] = row[4]
        row_values['snippet'] = row[5]
        all_values.append([[row[0]], [row[1]], [row[2]], [row[3]], [row[4]], [row[5]]])
    #    report_file.write("|".join(row) + "\n")
    # pprint.pprint(results)
    columns = ['A', 'B', 'C', 'D', 'E', 'F']
    cell_list = []
    for x in range(len(all_values)):
        width = str(2 + x)
        for y in columns:
            cell_list.append(pygsheets.Cell(y + width))

        wks.update_values(cell_list=cell_list, values=all_values[x], extend=True)
        # pprint.pprint(all_values[x])

    return 'report to /home/users/jeffderb/db/error_report'


if __name__ == '__main__':
    push()
