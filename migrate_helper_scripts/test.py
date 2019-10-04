import list_logs as list_logs
import archive_logs as archive_logs
import pprint

files = archive_logs.archive('archive-with-errors', ['VPV000', 'VPV001', 'VPV002'])

pprint.pprint(files)
