""" Enstore Env as dictionary """


import os

ENSTORE_ENV = dict(
    ENSTORE_OUT='/var/log/enstore',
    ENSTORE_MAIL='enstore-auto@fnal.gov',
    QPID_DIR='/opt/enstore/qpid',
    GADFLY_GRAMMAR='/opt/enstore/gadfly',
    CVSROOT='hppccvs@cdcvs.fnal.gov:/cvs/hppc',
    PYTHONUNBUFFERED='x',
    PYTHON_DIR='/opt/enstore/Python',
    ENSTORE_HOME='/home/enstore',
    ENSSH='/usr/bin/ssh',
    ENSTORE_SFA_POLICY='/home/enstore/site_specific/config/stken_policy.py',
    ENSCP='/usr/bin/scp',
    ENSTORE_CONFIG_HOST='stkensrv7n.fnal.gov',
    ENSTORE_GIT='ssh://p-enstore@cdgit.fnal.gov/cvs/projects/enstore',
    ENSTORE_CONFIG_DIR='/home/enstore/site_specific',
    ENSTORE_CONF_GIT='ssh://p-enstore-config@cdgit.fnal.gov/cvs/projects/enstore-config',
    PYTHONINC='/opt/enstore/Python/include/python2.7',
    ENSTORE_CONFIG_PORT=7500,
    ENSTORE_CONFIG_FILE='/home/enstore/site_specific/config/stk.conf',
    SWIG_LIB='/opt/enstore/SWIG/swig_lib',
    FTT_DIR='/opt/enstore/FTT',
    PYTHONPATH='/opt/enstore:/opt/enstore/src:/opt/enstore/modules:/opt/enstore/HTMLgen:'
               '/opt/enstore/PyGreSQL',
    PYTHONLIB='/opt/enstore/Python/lib/python2.7',
    FARMLETS_DIR='/usr/local/etc/farmlets',
    ENSTORE_DIR='/opt/enstore',
    ENSTORE_GANG='stken',
    SWIG_DIR='/opt/enstore/SWIG', **os.environ
)

ENSTORE_ENV['PATH'] = '/opt/enstore/Python/bin:/opt/enstore/sbin:/opt/enstore/bin:' \
                      '/opt/enstore/tools:/opt/enstore/qpid/bin:/opt/enstore/SWIG'
