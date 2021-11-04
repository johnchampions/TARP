from flask import current_app
from sqlalchemy.log import echo_property
from config import SQLALCHEMY_DATABASE_URI as dbstring
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


#engine = create_engine('mysql+pymysql://flasky:Merkin12@172.31.112.1:3306/flasky', echo=False, future=True)
engine = create_engine('mysql+pymysql://flask:Merkin12@flaskydb.ckzo2f8bjq9z.ap-southeast-2.rds.amazonaws.com:3306/flasky', echo=False, future=True)
#engine = create_engine(dbstring, echo=False, future=True)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from . import models
    Base.metadata.create_all(bind=engine)


