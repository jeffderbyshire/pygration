#!/bin/bash
MAILTO=jeffderb@fnal.gov
source /home/enstore/.bashrc
for f in /var/migration/scans/*; do
  bash "$f" -H || break  # execute successfully or break
  # Or more explicitly: if this execution fails, then stop the `for`:
  # if ! bash "$f" -H; then break; fi
done
