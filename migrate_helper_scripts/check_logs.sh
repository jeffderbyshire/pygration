#!/bin/bash
MAILTO=jeffderb@fnal.gov
/opt/miniconda3/bin/conda activate base
python /root/migration_scripts/tape-migration/pygration.py --process check --quiet
exit