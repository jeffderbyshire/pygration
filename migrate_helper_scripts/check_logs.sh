#!/bin/bash
MAILTO=jeffderb@fnal.gov
source /opt/miniconda3/etc/profile.d/conda.sh
/opt/miniconda3/bin/conda activate base
python /root/migration_scripts/tape-migration/pygration.py --process check --quiet
exit