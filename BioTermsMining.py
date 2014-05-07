from __future__ import division
from DataFilesDb import DataFilesDb
from RelationsDb import RelationsDb
from PublicationsDb import PublicationsDb
from PeopleDb import PeopleDb
from UsersDb import UsersDb
from PubMedSearcher import PubmedSearcher
import pandas
import sqlsoup
from termine_services import *
from Bio.Entrez import efetch
import sets
from sqlsoup import Session
from datetime import *

globalDB = sqlsoup.SQLSoup('mysql+mysqldb://root:@127.0.0.1/sysmo?charset=ascii')

__author__ = 'kristian'

#  export VERSIONER_PYTHON_PREFER_32_BIT=yes

class DataTableView:
    def __init__(self):
        db = globalDB
        # self.table_object = table_object
        s = db.execute("SELECT * \
            FROM data_files \
            LEFT JOIN data_files_projects \
            ON data_files.id=data_files_projects.data_file_id;")
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()
        self.view["terms"] = ""
        # self.view = self.view[self.view["contributor_type"] == "User"]
        self.terms = 0

    def get_terms_db(self, ids):
        self.view.terms[self.view.id.isin(ids)] = self.view[self.view.id.isin(ids)].apply(
            lambda row: TermsBag().termine_service(row['title'] + ". " + row['description']), axis=1)


class PublicationView:
    def __init__(self, table_object):
        db = globalDB
        self.table_object = table_object
        s = db.execute("SELECT * FROM publications")
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()
        self.view["terms"] = ""
        self.terms = 0

    def get_terms_db(self, ids):
        self.view.terms[self.view.id.isin(ids)] = self.view[self.view.id.isin(ids)].apply(
            lambda row: TermsBag().termine_service(row['title'] + ". " + row['description']), axis=1)


class Publication:
    def __init__(self):
        self.email = "garzaguk@cs.man.ac.uk"
        users_object = UsersDb()
        self.users = users_object.getRows()
        people_object = PeopleDb()
        self.people = people_object.getRows()
        self.db = globalDB
        relations_object = RelationsDb()
        self.relations = relations_object.getRows()
        publications_object = PublicationsDb()
        self.publications = publications_object.getRows()
        self.model_view = ModelTableView()
        self.assets = AssetsView().assets

    def get_used_items(self, pubmed_id):
        """

        :type pubmed_id: basestring
        """

        def windchill(resource_type):
            if resource_type == 1:
                return "Model"
            if resource_type == 2:
                return "DataFile"
            if resource_type == 3:
                return "DataFile"
            if resource_type == 4:
                return "DataFile"

        contributors_ids = self.ask_pubmed_authors(pubmed_id)
        users = UserTableView(self.db.users)
        contributors_disciplines = users.view[users.view.id.isin(contributors_ids)]
        involved_disciplines = contributors_disciplines.drop_duplicates(cols='discipline_id')
        involved_disciplines['resource_type'] = involved_disciplines.apply(lambda row: windchill(row["discipline_id"]), axis=1)
        return involved_disciplines

    def ask_pubmed_authors(self, pubmed_id):
        """

        :param pubme_ids:
        """
        pubmed_object = PubmedSearcher(self.email)
        names = pubmed_object.get_authors_list(pubmed_id)
        concatenated = pandas.DataFrame.merge(self.users, self.people, how='left', left_on='person_id', right_on='id',
                                              left_index=False, right_index=False, sort=True,
                                              suffixes=('_x', '_y'), copy=True)

        filtered = concatenated[concatenated.last_name.isin(names["LastName"])]
        r = filtered["contributor_id"]

        if 0 == filtered.shape[0]:
            print("No Results ask_publication_authors")

        assert isinstance(r, pandas.Series)
        return r

    def get_corpora(self, pubmed_id):
        """
        :param pubmed_id:
        :return:
        """
        # publication = pandas.DataFrame.from_csv('/Users/kristian/Desktop/' + pubmed_id, sep='\t')


        handle = efetch(db='pubmed', id=pubmed_id, retmode='text', rettype='abstract', email='garzaguk@.cs.man.ac.uk')
        text = handle.read()

        terms = TermsBag()
        terms.termine_service(text)
        publication = terms.to_data_frame()

        #
        # text = open('/Users/kristian/Desktop/' + pubmed_id + "m")
        #
        # terms = TermsBag()
        # terms.termine_service(text.read())
        # publication = terms.to_data_frame()


        assert isinstance(publication, pandas.DataFrame)
        return publication

    def get_data_sharing_ratio(self, pubmed_id):
        """

        :type pubmed_id: basestring
        """
        used_items = self.get_used_items(pubmed_id)
        shared_items = self.get_data_available(pubmed_id)
        print(shared_items.shape[0])
        print(used_items.shape[0])
        print("DS Ratio:", (shared_items.shape[0] / used_items.shape[0]))
        print(shared_items)
        # def get_used_items(self,pubmed_id):
        # authors = self.ask_publication_authors(self, pubmed_id)
        # authors
        return shared_items

    def get_data_available(self, pubmed_id):
        contributor_ids = self.ask_pubmed_authors(pubmed_id)
        # filtered = self.assets[self.assets.contributor_id.isin(contributor_ids)]
        # self.model_view.get_terms_db(filtered["id"])
        # descriptions = self.assets[self.assets.contributor_id.isin(contributor_ids)]
        filtered = self.model_view.view[self.model_view.view.contributor_id.isin(contributor_ids)]
        self.model_view.get_terms_db(filtered["id"])
        descriptions = self.model_view.view[self.model_view.view.contributor_id.isin(contributor_ids)]
        # # descriptions = self.get_descriptions(contributors_ids)
        publications = self.get_corpora(pubmed_id)
        shared_items = self.get_matching_terms(descriptions, publications)
        return shared_items

    def get_matching_terms(self, descriptions, publication):

        descriptions['no_similar_terms'] = 0
        compared2 = 0

        def windchill(terms):
            df_terms = TermsBag(text=terms)
            df_terms = df_terms.to_data_frame()
            compared = df_terms[df_terms.terms.isin(publication["terms"])]
            return compared.shape[0]


        def find_term_app(descriptions):
            return descriptions[descriptions["no_similar_terms"] != 0]

        def max_term_app(descriptions):
            return descriptions[descriptions["no_similar_terms"] == descriptions["no_similar_terms"].max()]

        def max_half_term_app(descriptions):
            """
                Get the assets with the more number of similar terms to the paper and a bit more
            :param descriptions:
            :return:
            """
            return descriptions[descriptions["no_similar_terms"] >= (descriptions["no_similar_terms"].max() / 2)]

        try:
            descriptions['no_similar_terms'] = descriptions.apply(lambda row: windchill(row['terms']), axis=1)
            compared2 = max_half_term_app(descriptions)
        except ValueError:
            print("lalala")

        return compared2

    def get_efficiency_coeff(self, pubmed_id, asset_ids):
        r = 0

        publication = self.publications[self.publications.pubmed_id.isin([int(pubmed_id)])]
        pubmed_id_relations = self.relations[self.relations.object_id.isin(publication["id"])]
        pubmed_id_relations = pubmed_id_relations[pubmed_id_relations["subject_type"] == "Model"]
        # pubmed_id_relations = pubmed_id_relations[pubmed_id_relations["subject_type"] == "DataFile"]

        matched = pubmed_id_relations[pubmed_id_relations.subject_id.isin(asset_ids)]
        not_matched = pubmed_id_relations[~pubmed_id_relations.subject_id.isin(asset_ids)]
        predicted = asset_ids.shape[0]
        ground_truth = pubmed_id_relations.shape[0]

        true_positives = matched.shape[0]

        false_positives = abs(predicted - true_positives)

        false_negatives = abs(not_matched.shape[0])

        print(true_positives, false_negatives, asset_ids.shape[0], ground_truth)

        try:
            precision = true_positives / (true_positives + false_positives)
            recall = true_positives / (true_positives + false_negatives)
            r = [{'pubmed_id': pubmed_id, 'recall': recall, 'precision': precision}]
        except ZeroDivisionError:
            print "Oops!  ZeroDivisionError  Try again..."
        else:
            print("Recall: ", recall)
            print("Precision: ", precision)

        return r

    def get_recall(self, pubmed_id):
        r = 0
        try:
            # contributor_ids = self.ask_pubmed_authors(pubmed_id)
            #
            # filtered = self.model_view.view[self.model_view.view.contributor_id.isin(contributor_ids)]
            # self.model_view.get_terms_db(filtered["id"])
            # descriptions = self.model_view.view[self.model_view.view.contributor_id.isin(contributor_ids)]
            #
            # publications = self.get_corpora(pubmed_id)
            # compared = self.get_matching_terms(descriptions, publications)

            compared = self.get_data_available(pubmed_id)

            r = self.get_efficiency_coeff(pubmed_id, compared["id"])
        except TypeError:
            print("TypeError")
        return r


class ModelTableView:
    def __init__(self):
    # def __init__(self, table_object):
        db = globalDB
        # self.table_object = table_object
        s = db.execute("SELECT models.model_type_id, models.contributor_type, models.id, models.contributor_id, models.title, models.description, \
            model_types.title  as type_title, models_projects.project_id \
            FROM models \
            LEFT JOIN model_types \
            ON models.model_type_id=model_types.id \
            LEFT JOIN models_projects \
            ON models.id=models_projects.model_id;")
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()
        self.view["terms"] = ""
        # print self.view.columns
        # self.view = self.view[self.view["contributor_type"] == "User"]
        self.terms = 0


    def get_terms_db(self, ids):
        self.view.terms[self.view.id.isin(ids)] = self.view[self.view.id.isin(ids)].apply(
            lambda row: TermsBag().termine_service(
                row['title'] + ". " + row['description'] + " . " + str(row['type_title'])), axis=1)


class UserTableView:
    def __init__(self, table_object):
        self.table_object = table_object
        self.db = globalDB
        s = self.db.execute("SELECT users.*, disciplines_people.discipline_id \
            FROM users \
            LEFT JOIN disciplines_people \
            ON disciplines_people.person_id = users.person_id;")
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()

class ProjectSubsTableView:
    def __init__(self):
        self.db = globalDB
        s = self.db.execute("SELECT  project_subscriptions.person_id, project_subscriptions.project_id, \
                            users.id as user_id, users.created_at \
                            FROM project_subscriptions \
                            LEFT JOIN users \
                            ON project_subscriptions.person_id = users.person_id;")
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()


class Project:
    def __init__(self):
        pass

    def get_members(self, id):
        subs = ProjectSubsTableView()
        subscriptions = subs

        members = subscriptions.view[subscriptions.view["project_id"] == id]

        #Filter New Members
        members["created_at"] = pandas.to_datetime(members["created_at"])
        members = members[members["created_at"] < datetime(2013, 1, 1)]

        return members["user_id"]

    def get_sharing_ratio(self, id):
        b = AssetsView()
        def lala(id):
            print id
            b = Asset(id["asset_id"])
            return b.get_permission_label()
        b.assets = b.assets[b.assets["project_id"] == id]
        b.assets['label'] = ""
        b.assets['label'] = b.assets.apply(lambda row:lala(row), axis=1)
        grpA  = b.assets.groupby('project_id')
    # for i in list([1,2,3,5,6,8,9,10,11,12,14,15]):
        project = grpA.get_group(id)
        total = len(project)
        open = len(project[project["label"] == 'open'])
        intra = len(project[project["label"] == 'intra'])
        inter = len(project[project["label"] == 'inter'])
        ratio = (intra+open+inter)/total
        return ratio



class ProjectTableView:
    def __init__(self):
        self.db = globalDB
        s = self.db.execute("SELECT * FROM projects")
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()

    def get_members(self, id):
        subscriptions = TableView('project_subscriptions')
        members = subscriptions.view[subscriptions.view["project_id"] == id]
        return members["person_id"]

class DataFilesProjectsTableView:
    def __init__(self):
        self.db = globalDB
        s = self.db.execute("SELECT * FROM data_files_projects")
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()

class AssetsTableView:
    def __init__(self):
        self.db = globalDB
        s = self.db.execute("SELECT * FROM assets")
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()

class AssetsView:
    def __init__(self):
        self.db = globalDB
        model_view = modelTableView
        data_view = dataTableView
        df1 = model_view.view[["title", "description", "contributor_id", "type_title", "id", 'project_id']]
        df2 = data_view.view[['title', 'description', 'contributor_id', 'id','project_id']]
        df1['resource_type'] = 'Model'
        df2['resource_type'] = 'DataFile'
        self.assets = pandas.concat([df2, df1], ignore_index=True)
        self.assets['asset_id'] = range(1, len(self.assets)+1)
        model_auth_view = TableView("model_auth_lookup")
        data_auth_view = TableView("data_file_auth_lookup")
        df1 = model_auth_view.view
        df2 = data_auth_view.view
        df1['resource_type'] = 'Model'
        df2['resource_type'] = 'DataFile'
        df1 = df1.rename(columns = {'asset_id':'id'})
        m = self.assets[self.assets["resource_type"] == "Model"]
        merge_models = pandas.DataFrame.merge(df1, m[list(['id','asset_id'])], how='left', on='id',
            left_index=True, right_index=False, sort=False,
            suffixes=('_x', '_y'), copy=False)
        df2 = df2.rename(columns = {'asset_id':'id'})
        m = self.assets[self.assets["resource_type"] == "DataFile"]
        merge_datafiles = pandas.DataFrame.merge(df2, m[list(['id','asset_id'])], how='left', on='id',
                                      left_index=True, right_index=False, sort=True,
                                      suffixes=('_x', '_y'), copy=False)

        self.permissions = pandas.concat([merge_datafiles, merge_models], ignore_index=True)

class Asset:
    def __init__(self, id):
        self.id = id
    #
    #
    # def get_info(self):
        a = assetsView
        self.info = a.assets[a.assets["asset_id"] == self.id]
        self.access = ""
        self.project = int(self.info["project_id"])
        self.permissions = a.permissions[a.permissions["asset_id"] == self.id]


        # self.info = self.info.reset_index(drop=True)
        # self.info = self.info.to_dict('records')
        # self.info = self.info.to_dict()
        # print self.info

    def get_permission_label(self):
        # a = AssetsView()
        # self.get_info()
        # self.permissions = a.permissions[a.permissions["asset_id"] == self.id]
        # access = self.permissions[self.permissions["can_download"] == 1]
        access = self.permissions[self.permissions["can_view"] == 1]

        access = self.remove_sysmodb_permissions(access)

        self.access = self.is_open(access)

        if not self.access:
            self.access = self.is_intra(access)
        if not self.access:
            self.access = self.is_partial_intra(access)
        if not self.access:
            self.access = self.is_private(access)
        if not self.access:
            self.access = self.is_inter(access)
        if not self.access:
            self.access = self.is_ext_private(access)

        # print "lolo"
        # print access


        return self.access


    @staticmethod
    def is_open(permissions):
        r = permissions[permissions.user_id.isin([0])]
        if r.shape[0] :
            return "open"
        return ""

    @staticmethod
    def is_private(permissions):
        if permissions.shape[0] == 1 and len(permissions[permissions["can_delete"] == 1]) > 0:
            return "private"
        return ""

    @staticmethod
    def is_ext_private(permissions):

        # print permissions
        if len(permissions[permissions["can_delete"] == 1]) > 0:
            return "extended private"
        return ""


    def is_intra(self, permissions):
        projects = Project()
        project_members = projects.get_members(self.project)

        if set(permissions["user_id"]).issubset( set(project_members) ) and \
                len(permissions["user_id"]) == len(project_members):
            return "intra"
        return ""

    def is_partial_intra(self, permissions):
        projects = Project()
        project_members = projects.get_members(self.project)

        # print permissions["user_id"]
        # print project_members

        if set(permissions["user_id"]).issubset( set(project_members) ):
            return "partial_intra"
        return ""

    def is_inter(self, permissions):
        projects = Project()
        project_members = projects.get_members(self.project)

        if set(permissions["user_id"]).issuperset( set(project_members) ):
            return "inter"
        return ""

    def remove_sysmodb_permissions(self, permissions):
        if self.project != 12:
            print "lalaa"
            projects = Project()
            sysmodb_members = projects.get_members(12)
            permissions = permissions[~permissions.user_id.isin(sysmodb_members)]
        return permissions


class TableView:
    def __init__(self, table_name):
        self.db = globalDB
        s = self.db.execute("SELECT * FROM " + table_name)
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()

class Model(Asset):
    def __init__(self, id):
        self.id = id
        # table = TableView("models")
        table = modelTableView
        self.data = table.view[table.view["id"] == id]

    def get_project(self):
        m = TableView("models_projects")
        list = m.view[m.view.model_id.isin(self.data["id"])]
        self.data["project_id"] = list["project_id"].ix[1:]
        return self.data["project_id"]

    def get_asset_id(self):
        m = TableView("assets")
        m = m.view[m.view["resource_type"] == "model"]
        list = m[m.resource_id.isin(self.data["id"])]
        self.data["asset_id"] = list["id"].ix[1:]
        return self.data["asset_id"]

    def get_terms(self):
        self.data["terms"] = TermsBag().termine_service(str(self.data['title'] + ". " + self.data['description'] + " . " + str(self.data['type_title'])))
        return self.data["terms"]

class TermsBag:
    def __init__(self, text=" "):
        self.text = text
        self.terms = self.to_data_frame()

    def termine_service(self, text):
        port = termineLocator().gettermine_porttype()
        req = analyze_request()
        print ".."
        # print text
        decoded_str = text.decode('ISO-8859-1')
        encoded_str = decoded_str.encode('ascii', 'replace')

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

    def compare_with(self, terms_bag):
        self.to_data_frame(self.text)
        similarly = self.terms[self.terms.terms.isin(terms_bag.terms)]
        return similarly


dataTableView = DataTableView()
modelTableView = ModelTableView()
assetsView = AssetsView()

