#!/bin/bash
MAILTO=jeffderb@fnal.gov
eval "$(conda shell.bash hook)"
/opt/miniconda3/bin/conda activate base
python /root/migration_scripts/tape-migration/pygration.py --process check --quiet
exit