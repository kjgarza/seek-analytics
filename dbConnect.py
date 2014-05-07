import MySQLdb
import sqlsoup
import sys


sysmo_db = sqlsoup.SQLSoup('mysql+mysqldb://root:@127.0.0.1/sysmo?charset=ascii')


    # db = MySQLdb.connect(host="127.0.0.1",
    #                      user="root",
    #                      passwd="",
    #                      db="sysmo")
    # cursor = db.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute("SELECT VERSION()")
    # row = cursor.fetchone()
    # print "server version:", row[0]









__author__ = 'kristian'