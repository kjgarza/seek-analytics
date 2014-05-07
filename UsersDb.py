import MySQLdb as mdb
import pandas

class UsersDb:
    def __init__(self):


        db = mdb.connect(host="127.0.0.1",
                     user="root",
                     passwd="",
                     db="sysmo")

        self.name = "users"
        self.cursor = db.cursor(mdb.cursors.DictCursor)
        # self.cursor.execute("SELECT * FROM %s",(self.name))
        self.cursor.execute("SELECT * FROM users")

    # def getCell(self):

    def getColumn(self, column):
        """

        :param column:
        :return:
        """
        one = self.getRows
        assert isinstance(column, basestring)
        return one[column]

    def getRow(self,id):
        """



        :param id:
        """
        rows = self.cursor.fetchall()
        assert isinstance(id, basestring)
        return rows["id"]



    def getRows(self):
        """


        :return:
        """
        rows = self.cursor.fetchall()
        assert isinstance(rows, tuple)
        df =  pandas.DataFrame.from_records(rows)
        df.rename(columns={'id':'contributor_id'}, inplace=True)
        return df

__author__ = 'kristian'
