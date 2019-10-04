import list_logs as list_logs
import archive_logs as archive_logs
import pprint

files = list_logs.get_logs('archive-with-errors', ['VPV003', 'VPV004', 'VPV005'])

pprint.pprint(files)
