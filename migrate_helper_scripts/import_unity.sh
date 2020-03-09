#!/bin/bash
MAILTO=jeffderb@fnal.gov
source /opt/miniconda3/etc/profile.d/conda.sh
source /root/.bashrc
conda activate base
cd /root/migration_scripts/tape-migration
python pygration.py --process import --quiet >/dev/null 2>&1