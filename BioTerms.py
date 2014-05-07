from PubMedSearcher import *
import sqlsoup
import sqlalchemy
import pandas
from termine_services import *
from Bio.Entrez import efetch

db = sqlsoup.SQLSoup('mysql+mysqldb://root:@127.0.0.1/sysmo?charset=utf8')


class PublicationsView:
    def __init__(self):
        self.email = "garzaguk@cs.man.ac.uk"
        joinl = db.join(db.publications, db.users, isouter=True)


        # pubmed_object = PubmedSearcher(self.email)
        # self.pubmed_metadata = pubmed_object.get_authors_list(self.pubmed_id)

        db.publications['terms'] = db.publications.apply(
            lambda row: TermsBag.termine_service(row['title'] + " " + row['description']), axis=1)


    def ask_termine_terms(self, text):
        r = TermsBag.termine_service(text)


    def get_publication_info(self, pubmed_id):
        return self.publication


class DataAssetsView:
    def __init__(self):
        db.data_files.terms = db.data_files.apply(
            lambda row: TermsBag.termine_service(row['title'] + " " + row['description']), axis=1)
        self.view = db.data_files

    def get_view_dump(self):
        r = pandas.DataFrame(self.view)
        return r


class UsersView:
    def __init__(self):
        print(db.users.c)
        print(db.people.c)
        people = db.with_labels(db.people)


        self.view = db.join(db.users, people, db.users.persond_id==people.id, isouter=True).c.keys()

    def get_view_dump(self):
        r = pandas.DataFrame(self.view)
        return r


class TermsBag:
    def __init__(self, text=""):
        self.text = text
        self.terms = pandas.DataFrame()

    def termine_service(self, text):
        port = termineLocator().gettermine_porttype()
        req = analyze_request()
        print ".."
        decoded_str = text.decode("ISO-8859-1")
        encoded_str = decoded_str.encode("ascii", 'replace')
        # print encoded_str
        req._src = encoded_str
        res = port.analyze(req)
        self.text = res._result
        return res._result

    def to_data_frame(self):
        list_terms = self.text.encode('ascii', 'ignore').split('\n')
        for j, line in enumerate(list_terms):
            title_trans = ''.join(chr(c) if chr(c).isupper() or chr(c).islower() else ' ' for c in range(256))
            list_terms[j] = line.translate(title_trans).strip()
        df_terms = pandas.DataFrame(list_terms, columns=['terms'])
        self.terms = df_terms
        return df_terms

# a = UsersView()
# a.get_view_dump()

# models = pandas.DataFrame(db.models.all())


class Table:
    def __init__(self, table_object):
        self.table_object = table_object

    def modify_column_values(self, key_values_df):
        pass


class PublicationsTableView:
    def __init__(self, table_object):
        db = sqlsoup.SQLSoup('mysql+mysqldb://root:@127.0.0.1/sysmo?charset=utf8')
        self.table_object = table_object
        s = db.execute("SELECT * FROM publications")
        self.view  = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()
        self.view["terms"]= ""
        self.terms = 0

    def get_terms_file(self, pubmed_id):
        # self.view.terms[self.view.pubmed_id.isin([int(pubmed_id)])] = pandas.DataFrame.from_csv('/Users/kristian/Desktop/' + pubmed_id, sep='\t')

    def get_terms_abstract(self, pubmed_id):
        handle = efetch(db='pubmed', id=pubmed_id, retmode='text', rettype='abstract', email='garzaguk@.cs.man.ac.uk')
        text = handle.read()
        terms = TermsBag()
        # terms.termine_service(text)
        self.view.terms[self.view.pubmed_id.isin([int(pubmed_id)])] = terms.termine_service(text)
        self.terms = terms.to_data_frame()

    def get_terms_desktop(self, pubmed_id):
        text = open('/Users/kristian/Desktop/' + pubmed_id + "m")
        terms = TermsBag()
        # terms.termine_service(text.read())
        self.view.terms[self.view.pubmed_id.isin([int(pubmed_id)])] = terms.termine_service(text.read())
        self.terms = terms.to_data_frame()

class DataTableView:
    def __init__(self, table_object):
        db = sqlsoup.SQLSoup('mysql+mysqldb://root:@127.0.0.1/sysmo?charset=utf8')
        self.table_object = table_object
        s = db.execute("SELECT * FROM data_files")
        self.view  = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()
        self.view["terms"]= ""
        self.terms = 0

    def get_terms_db(self, ids):
        self.view.terms[self.view.id.isin(ids)] = self.view[self.view.id.isin(ids)].apply(lambda row: TermsBag().termine_service(row['title'] + " " + row['description']), axis=1)



# print(models)

__author__ = 'kristian'


a = PublicationsTableView(db.publications)
a.get_terms_file("22686585")
print a.view[a.view["pubmed_id"] == 22686585]