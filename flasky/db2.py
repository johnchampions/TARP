from flask import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config

#engine = create_engine('mysql+pymysql://flasky:Merkin12@localhost:3306/flasky', echo=False, future=True)

#engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=False, future=True)
engine = create_engine('mysql+pymysql://flask:Merkin12@flaskydb.ckzo2f8bjq9z.ap-southeast-2.rds.amazonaws.com:3306/flasky', echo=False, future=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()



def init_db():
    import flasky.models
    Base.metadata.create_all(bind=engine)


