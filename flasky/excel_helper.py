import pandas
import sqlite3
import db2

postcode = pandas.read_excel('instance/australian_postcodes.xls',
    sheet_name ='Sheet1',
    header = 0)

postcode.to_sql('postcode', db2.engine, if_exists='append', index=False)


