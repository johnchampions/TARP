import sqlite3
import datetime
#from flasky.db2 import db_session
import mysql.connector
from re import search





sqlitecon = sqlite3.connect('./instance/census2016_hihc_aus_short.gpkg')
cur = sqlitecon.cursor()
