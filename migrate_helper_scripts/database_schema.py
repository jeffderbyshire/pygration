""" database schema using sqlalchemy """

import logging
from collections import defaultdict
from configparser import ConfigParser
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, TIMESTAMP, Date
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
ENGINE = create_engine('postgresql+psycopg2://' + CONFIG['Default']['database'])
SESSION_FACTORY = sessionmaker(bind=ENGINE)
SESSION = scoped_session(SESSION_FACTORY)
BASE = declarative_base()
DEBUG = True


class Servers(BASE):
    """ Servers definition and methods """
    __tablename__ = 'servers'

    server_id = Column(Integer, primary_key=True)
    server = Column(String, unique=True, nullable=False)
    updated = Column(TIMESTAMP, default=func.now())

    def __init__(self, server):
        self.server = server

    def __repr__(self):
        return "<Servers(server='%s')>" % self.server


class Volumes(BASE):
    """ Volumes table definition and relationship to log_files """
    __tablename__ = 'volumes'

    volume_id = Column(Integer, primary_key=True)
    volume = Column(String, unique=True, nullable=False)
    updated = Column(TIMESTAMP, default=func.now())

    log_files = relationship("LogFiles", back_populates='volume',
                             cascade="all, delete, delete-orphan")
    bfid_errors = relationship("BFIDErrors", back_populates='volumes',
                               cascade="all, delete, delete-orphan")

    def __init__(self, volume):
        self.volume = volume

    def __repr__(self):
        return "<Volumes(volume='%s')>" % self.volume


class LogFiles(BASE):
    """ LogFiles table definition and relationship to volumes and log detail """
    __tablename__ = 'log_files'

    log_files_id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey("servers.server_id"), nullable=False)
    volume_id = Column(Integer, ForeignKey("volumes.volume_id"), nullable=False)
    log_file = Column(String, nullable=False)
    date = Column(String, nullable=False)
    updated = Column(TIMESTAMP, default=func.now())

    volume = relationship("Volumes", back_populates="log_files")
    log_file_detail = relationship("LogFileDetail", back_populates='log_files',
                                   cascade="all, delete, delete-orphan")

    def __init__(self, server_id, volume_id, log_file, date):
        self.server_id = server_id
        self.volume_id = volume_id
        self.log_file = log_file
        self.date = date

    def __repr__(self):
        return "<LogFiles(server_id='%s',volume_id='%s',log_file='%s',date='%s')>" % \
               self.server_id, self.volume_id, self.log_file, self.date


class LogFileDetail(BASE):
    """ Log File Detail table definition and relationship to log_files """
    __tablename__ = 'log_file_detail'

    log_file_detail_id = Column(Integer, primary_key=True)
    log_files_id = Column(Integer, ForeignKey("log_files.log_files_id"), nullable=False)
    snippet = Column(String, nullable=False)
    message = Column(String, nullable=False)
    updated = Column(TIMESTAMP, default=func.now())

    log_files = relationship("LogFiles", back_populates="log_file_detail")

    def __init__(self, log_files_id, snippet, message):
        self.log_files_id = log_files_id
        self.snippet = snippet
        self.message = message

    def __repr__(self):
        return "<LogFileDetail(snippet='%s',message='%s')>" % self.snippet, self.message


class BFIDErrors(BASE):
    """ BFID Errors table definition and relationship to volumes """
    __tablename__ = 'bfid_errors'

    bfid_errors_id = Column(Integer, primary_key=True)
    volume_id = Column(Integer, ForeignKey("volumes.volume_id"), nullable=False)
    bfid = Column(String, nullable=False)
    error = Column(String, nullable=False)
    updated = Column(TIMESTAMP, default=func.now())

    volumes = relationship("Volumes", back_populates="bfid_errors")

    def __repr__(self):
        return "<BFIDErrors(bfid='%s',error='%s')>" % self.bfid, self.error


class Migrated(BASE):
    """ Migrated Volumes to be checked to speed up fix archives """
    __tablename__ = 'migrated'

    migrated_id = Column(Integer, primary_key=True)
    volume = Column(String, nullable=False, unique=True)
    updated = Column(TIMESTAMP, default=func.now())

    def __repr__(self):
        return "<Migrated(volume='%s')>" % self.volume


class Running(BASE):
    """ Running volumes to be checked before reruns """
    __tablename__ = 'running'

    server = Column(String, nullable=False, primary_key=True)
    volume = Column(String, nullable=False, primary_key=True)
    updated = Column(TIMESTAMP, default=func.now())

    def __repr__(self):
        return "<Running(volume='%s')>" % self.volume


class Logging(BASE):
    """ Log Table details of each process / node """
    __tablename__ = 'logging'

    logging_id = Column(Integer, primary_key=True)
    server = Column(String, nullable=False)
    process = Column(String, nullable=False)
    log_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    updated = Column(TIMESTAMP, default=func.now())

    def __repr__(self):
        return "<Logging(server='%s',process='%s',log_type='%s',message='%s')>" % \
               self.server, self.process, self.log_type, self.message


class MigrationScan(BASE):
    """ Migration Scan table """
    __tablename__ = 'migration_scan'

    migration_scan_id = Column(Integer, primary_key=True)
    scan_volume = Column(String, nullable=False, unique=True)
    scan_start = Column(Date)
    scan_node = Column(String)
    scan_errors = Column(String)
    scan_end = Column(Date)
    source_list = Column(String)
    updated = Column(TIMESTAMP, default=func.now())

    def __repr__(self):
        return "<MigrationScan(scan_volume='%s',scan_start='%s',scan_node='%s',scan_errors='%s'," \
               "scan_end='%s',source_list='%s')>" % (self.scan_volume, self.scan_start,
                                                     self.scan_node, self.scan_errors,
                                                     self.scan_end, self.source_list)


def insert_update_migration_scan(record):
    """ insert or update migration scan """
    session = SESSION()
    skip_update = session.query(MigrationScan).filter_by(**record).first()
    if skip_update:
        pass
    else:
        result = session.query(MigrationScan).filter_by(scan_volume=record['scan_volume']).first()
        if result:
            for key, value in record.items():
                setattr(result, key, value)
        else:
            insert = MigrationScan(**record)
            session.add(insert)
        session.commit()


class MigrationState(BASE):
    """ Migration State table """
    __tablename__ = 'migration_state'

    migration_state_id = Column(Integer, primary_key=True)
    source_volume = Column(String, nullable=False, unique=True)
    media = Column(String)
    migration_type = Column(String)
    migration_start = Column(Date)
    node = Column(String)
    errors = Column(String)
    migration_end = Column(Date)
    destination_volumes = Column(String)
    scanned = Column(Date)
    storage_group = Column(String)
    library = Column(String)
    file_family = Column(String)
    updated = Column(TIMESTAMP, default=func.now())

    def __repr__(self):
        return "<MigrationState(source_volume='%s',media='%s',migration_type='%s'," \
               "migration_start='%s',node='%s',errors='%s',migration_end='%s'," \
               "destination_volumes='%s',scanned='%s',storage_group='%s',library='%s'," \
               "file_family='%s')>" % (self.source_volume, self.media, self.migration_type,
                                       self.migration_start, self.node, self.errors,
                                       self.migration_end,
                                       self.destination_volumes, self.scanned, self.storage_group,
                                       self.library, self.file_family)


def insert_update_migration_state(record):
    """ insert or update migration scan """
    session = SESSION()
    skip_update = session.query(MigrationState).filter_by(**record).first()
    if skip_update:
        pass
    else:
        result = \
            session.query(MigrationState).filter_by(source_volume=record['source_volume']).first()
        if result:
            for key, value in record.items():
                setattr(result, key, value)
        else:
            insert = MigrationState(**record)
            session.add(insert)
        session.commit()


def has_volume_been_scanned(volume):
    """ check scan table for volume and if scan has started """
    session = SESSION()
    return bool(session.query(MigrationScan).filter(
        MigrationScan.scan_volume == volume, MigrationScan.scan_start is None).count())


def get_volumes_need_scanning(storage_group):
    """ get volumes to scan based on storage group """
    volumes_need_scanning = defaultdict(list)
    session = SESSION()
    result = \
        session.query(MigrationState).filter(
            MigrationState.storage_group == storage_group,
            MigrationState.migration_end is not None).order_by(
                MigrationState.storage_group, MigrationState.file_family).all()
    if DEBUG:
        logging.info("volumes need scanning results %s", result)
    for row in result:
        volumes = row.destination_volumes.split()
        file_family = row.file_family
        for volume in volumes:
            insert_update_migration_scan({"scan_volume": volume})
            if not has_volume_been_scanned(volume):
                volumes_need_scanning[file_family].append(volume)

    return volumes_need_scanning


def get_node_id(node_name):
    """ add node name and return node id """
    session = SESSION()
    node = Servers(server=node_name)
    server = session.query(Servers).filter_by(server=node_name).first()
    if not server:
        session.add(node)
        session.commit()
        server = session.query(Servers).filter_by(server=node_name).first()
    return server.server_id


def get_volume_id(volume_name):
    """ add volume and return volume id """
    session = SESSION()
    volume = Volumes(volume=volume_name)
    volume_record = session.query(Volumes).filter_by(volume=volume_name).first()
    if not volume_record:
        session.add(volume)
        session.commit()
        volume_record = session.query(Volumes).filter_by(volume=volume_name).first()
    return volume_record.volume_id


def get_log_file_id(server_id, volume_id, log_file, date):
    """ add log file and return log id """
    session = SESSION()
    log_file_insert = LogFiles(server_id=server_id, volume_id=volume_id, log_file=log_file,
                               date=date)
    session.add(log_file_insert)
    session.commit()

    log_file_record = session.query(LogFiles).filter_by(server_id=server_id, volume_id=volume_id,
                                                        log_file=log_file, date=date).first()
    return log_file_record.log_files_id


def insert_migrated(volume):
    """ insert volume into migrated table """
    session = SESSION()
    migrated_volume = Migrated(volume=volume)
    session.add(migrated_volume)
    session.commit()


def insert_log_file_detail(log_details):
    """ insert multiple log file detail records """
    session = SESSION()
    for log in log_details:
        insert = LogFileDetail(log_files_id=log[0], snippet=log[1], message=log[2])
        session.add(insert)
    session.commit()


def delete_volume_name(volume_name):
    """ delete from all where volume_name """
    session = SESSION()
    volume_delete = session.query(Volumes).filter_by(volume=volume_name).delete()
    session.commit()
    return volume_delete


def insert_bfid_errors(volume_id, bfid, message):
    """ insert multiple bfid errors into table """
    session = SESSION()
    insert = BFIDErrors(volume_id=volume_id, bfid=str(bfid), error=str(message))
    session.add(insert)
    session.commit()


def volume_id_in_bfid_errors(volume_id):
    """ check bfid errors for volume_id """
    session = SESSION()
    return bool(session.query(BFIDErrors).filter(BFIDErrors.volume_id == volume_id).count())


def volume_is_migrated(volume):
    """ check if volume serial exists in migrated table """
    session = SESSION()
    return bool(session.query(Migrated).filter(Migrated.volume == volume).count())


def does_bfid_exist(bfid):
    """ check if bfid exists in bfid errors table """
    session = SESSION()
    return bool(session.query(BFIDErrors).filter(BFIDErrors.bfid == bfid).count())


def update_running(server, volumes):
    """ remove server entries and insert current running volumes """
    session = SESSION()
    session.query(Running).filter_by(server=server).delete()
    session.commit()
    for volume in volumes:
        insert = Running(server=server, volume=volume)
        session.add(insert)
    session.commit()


def get_running():
    """ get volumes from table running """
    session = SESSION()
    return session.query(Running.volume).all()


def insert_log(server, process, log_type, message):
    """ insert log message into log """
    session = SESSION()
    insert = Logging(server=server, process=process, log_type=log_type, message=message)
    session.add(insert)
    session.commit()
