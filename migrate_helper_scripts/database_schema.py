""" database schema using sqlalchemy """

from configparser import ConfigParser
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
ENGINE = create_engine('sqlite:///' + CONFIG['Default']['sqlite_db'])
SESSION = sessionmaker(bind=ENGINE)
BASE = declarative_base()


class Servers(BASE):
    """ Servers definition and methods """
    __tablename__ = 'servers'

    server_id = Column(Integer, primary_key=True)
    server = Column(String, unique=True, nullable=False)

    def __init__(self, server):
        self.server = server

    def __repr__(self):
        return "<Servers(server='%s')>" % self.server


class Volumes(BASE):
    """ Volumes table definition and relationship to log_files """
    __tablename__ = 'volumes'

    volume_id = Column(Integer, primary_key=True)
    volume = Column(String, unique=True, nullable=False)

    log_files = relationship("LogFiles", back_populates='volume',
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

    log_files = relationship("LogFiles", back_populates="log_file_detail")

    def __init__(self, log_files_id, snippet, message):
        self.log_files_id = log_files_id
        self.snippet = snippet
        self.message = message

    def __repr__(self):
        return "<LogFileDetail(snippet='%s',message='%s')>" % self.snippet, self.message


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