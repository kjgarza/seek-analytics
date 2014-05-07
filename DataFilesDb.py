import MySQLdb as mdb
import pandas


class DataFilesDb:
    def __init__(self):



        db = mdb.connect(host="127.0.0.1",
                     user="root",
                     passwd="",
                     db="sysmo")

        self.name = "data_files"
        self.cursor = db.cursor(mdb.cursors.DictCursor)
        # self.cursor.execute("SELECT * FROM %s",(self.name))
        self.cursor.execute("SELECT * FROM data_files")

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
        return df



# a = DataFilesDB()
# s = a.getRows()
# print(type(s))
# print(s['contributor_id'])
# print(s[s.contributor_id.isin([13, 150, 88,])])
# print(s.query('contributor_id == ["13", "150", "88"]'))


# for row in s:
#     print row["contributor_id"]

# import pandas
#
# df =  pandas.DataFrame.from_records(s)
# print(df['contributor_type'])
# print(df[5:10])
#
# db = sqlsoup.SQLSoup('mysql+mysqldb://root:@127.0.0.1/sysmo?charset=utf8')
#
# users_tbl = db.users
#
# type(users_tbl)

__author__ = 'kristian'
