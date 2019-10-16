#!/bin/bash
MAILTO=jeffderb@fnal.gov
conda activate
cd /root/migration_scripts/tape-migration
python pygration.py --process check --quiet
exit