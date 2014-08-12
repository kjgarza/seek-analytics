from __future__ import division
from PubMedSearcher import PubmedSearcher
import pandas
import sqlsoup
from termine_services import *
from Bio.Entrez import efetch
import sets
from sqlsoup import Session
from datetime import *
import MySQLdb
import pandas.io.sql as psql
import unidecode


globalDB = sqlsoup.SQLSoup('mysql+mysqldb://root:@127.0.0.1/sysmo?charset=ascii')

__author__ = 'kristian'

#  export VERSIONER_PYTHON_PREFER_32_BIT=yes

class DataTableView:
    def __init__(self):
        db = globalDB
        # self.table_object = table_object
        s = db.execute("SELECT * \
            FROM data_files_copy \
            LEFT JOIN data_files_projects \
            ON data_files_copy.id=data_files_projects.data_file_id;")
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()
        # self.view["terms"] = ""
        # self.view = self.view[self.view["contributor_type"] == "User"]
        self.terms = 0

    def get_terms_db(self, ids):
        self.view.terms[self.view.id.isin(ids)] = self.view[self.view.id.isin(ids)].apply(
            lambda row: TermsBag().termine_service(row['title'] + ". " + row['description']), axis=1)


class PublicationView:
    def __init__(self):
        db = globalDB
        s = db.execute("SELECT * FROM publications_copy \
            LEFT JOIN projects_publications \
            ON projects_publications.publication_id = publications_copy.id;")
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()
        self.view = self.view[self.view['pubmed_id'].notnull()]
        self.view["terms"] = ""
        self.terms = 0

    def get_terms_db(self, ids):
        self.view.terms[self.view.id.isin(ids)] = self.view[self.view.id.isin(ids)].apply(
            lambda row: TermsBag().termine_service(row['title'] + ". " + row['description']), axis=1)

    def fill_ds_ratio(self):
        self.view["ds_ratio"] = 0.0
        self.view["ds_ratio"] = self.view.apply(lambda row: Publication(str(int(row["pubmed_id"]))).get_data_sharing_ratio(), axis=1)


class Publication:
    def __init__(self, pubmed_id):
        if not isinstance(pubmed_id, str):
            raise TypeError("pubmed_id must be set to an string")
        self.pubmed_id = pubmed_id
        self.email = "garzaguk@cs.man.ac.uk"
        # users_object = UsersDb()
        self.users = UserTableView().view
        # people_object = PeopleDb()
        self.people = TableView("people").view
        self.db = globalDB
        # relations_object = RelationsDb()
        self.relations = TableView("relationships").view
        # publications_object = PublicationsDb()
        self.publications = TableView("publications").view
        self.model_view = modelTableView
        self.assets = assetsView

    def get_quantity_used_items(self):
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


        users = UserTableView()

        contributors_ids = self.get_authors()
        if not len(contributors_ids):
            return users.view[0:0]


        contributors = users.view[users.view.id.isin(contributors_ids)]
        involved_disciplines = contributors.drop_duplicates(cols=['discipline_id', 'institution_id'])
        involved_disciplines['resource_type'] = involved_disciplines.apply(lambda row: windchill(row["discipline_id"]),
                                                                           axis=1)
        return involved_disciplines[['discipline_id', 'institution_id', 'resource_type']]

    def get_authors(self):
        """

        :param pubme_ids:
        """
        pubmed_object = PubmedSearcher(self.email)
        names = pubmed_object.get_authors_list(self.pubmed_id)
        # self.users["contributor_id"] = self.users["id"]
        # concatenated = pandas.DataFrame.merge(self.users, self.people, how='left', left_on='person_id', right_on='id',
        #                                       left_index=False, right_index=False, sort=True,
        #                                       suffixes=('_x', '_y'), copy=True)


        concatenated = self.users
        concatenated["contributor_id"] = concatenated["id"]
        filtered = concatenated[concatenated.last_name.isin(names["LastName"])]

        r = filtered["contributor_id"]

        if 0 == filtered.shape[0]:
            print("No Results ask_publication_authors")

        assert isinstance(r, pandas.Series)
        return r

    def get_corpora(self):
        """
        :param pubmed_id:
        :return:
        """
        # publication = pandas.DataFrame.from_csv('/Users/kristian/Desktop/' + self.pubmed_id, sep='\t')


        # handle = efetch(db='pubmed', id=self.pubmed_id, retmode='text', rettype='abstract',
        #                 email='garzaguk@.cs.man.ac.uk')
        # text = handle.read()

        pub = (self.publications[self.publications['pubmed_id'] == int(self.pubmed_id)]).squeeze()

        text = pub['abstract']

        terms = TermsBag()
        terms.termine_service(text)
        publication = terms.to_data_frame()

        #
        # text = open('/Users/kristian/Desktop/' + self.pubmed_id + "m")
        #
        # terms = TermsBag()
        # terms.termine_service(text.read())
        # publication = terms.to_data_frame()


        assert isinstance(publication, pandas.DataFrame)
        return publication

    def get_data_sharing_ratio(self):
        """

        :type pubmed_id: basestring
        """
        used_items = self.get_quantity_used_items()
        shared_items = self.get_data_available()

        if not len(shared_items):
            return 0

        used_models = len((used_items[used_items["resource_type"] == 'Model'])['institution_id'].unique())
        used_files = len((used_items[used_items["resource_type"] == 'DataFile'])['institution_id'].unique())


        # print shared_items

        ava_models = len(shared_items[shared_items["resource_type"] == 'Model'])
        ava_files =len(shared_items[shared_items["resource_type"] == 'DataFile'])

        if not used_models:
            m = 0
        elif used_models < ava_models:
            m = 1
        else:
            m = ava_models/used_models
        if not used_files:
            d = 0
        elif used_files < ava_files:
            d = 1
        else:
            d = ava_files/used_files

        print m
        print d

        print used_models
        print used_files


        ### average of the ratios
        r = (m+d)/(used_files/used_files + used_models/used_models)

        ####ratio of the averages
        # r = (ava_files + ava_models)/(used_files + used_models)

        # r = (shared_items.shape[0] / used_items.shape[0])
        return r

    def get_data_available(self):
        contributor_ids = self.get_authors()

        if not len(contributor_ids):
            return self.assets.assets[0:0]

        filtered = self.assets.assets[self.assets.assets.contributor_id.isin(contributor_ids)]

        # filtered['label'] = ""
        # filtered['label'] = filtered.apply(lambda row: Asset(row["asset_id"]).get_permission_label(), axis=1)
        filtered = filtered[filtered['access'] == 'open']

        if not len(filtered):
            return filtered

        # filtered["terms"] = filtered.apply(lambda row: Asset(row['asset_id']).get_terms(), axis=1)
        # print filtered["terms"]
        descriptions = filtered

        # filtered = self.model_view.view[self.model_view.view.contributor_id.isin(contributor_ids)]
        # self.model_view.get_terms_db(filtered["id"])
        # descriptions = self.model_view.view[self.model_view.view.contributor_id.isin(contributor_ids)]
        # # descriptions = self.get_descriptions(contributors_ids)
        publications = self.get_corpora()
        shared_items = self.__get_matching_terms(descriptions, publications)
        return shared_items

    def __get_matching_terms(self, descriptions, publication):
        if not isinstance(descriptions, pandas.DataFrame):
            raise TypeError("descriptions must be set to an pandas.DataFrame")
        if not isinstance(publication, pandas.DataFrame):
            raise TypeError("publication must be set to an pandas.DataFrame")
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

            print descriptions

            descriptions['no_similar_terms'] = descriptions.apply(lambda row: windchill(row['terms']), axis=1)
            compared2 = max_half_term_app(descriptions)
        except ValueError:
            print("lalala")

        return compared2

    def get_efficiency_coeff(self, asset_ids):
        if not isinstance(asset_ids, pandas.DataFrame):
            raise TypeError("asset_ids must be set to an pandas.DataFrame")
        r = 0

        publication = self.publications[self.publications.pubmed_id.isin([int(self.pubmed_id)])]
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
            r = [{'pubmed_id': self.pubmed_id, 'recall': recall, 'precision': precision}]
        except ZeroDivisionError:
            print "Oops!  ZeroDivisionError  Try again..."
        else:
            print("Recall: ", recall)
            print("Precision: ", precision)

        return r

    def get_recall(self):
        r = 0
        try:
            # contributor_ids = self.ask_pubmed_authors(self.pubmed_id)
            #
            # filtered = self.model_view.view[self.model_view.view.contributor_id.isin(contributor_ids)]
            # self.model_view.get_terms_db(filtered["id"])
            # descriptions = self.model_view.view[self.model_view.view.contributor_id.isin(contributor_ids)]
            #
            # publications = self.get_corpora(self.pubmed_id)
            # compared = self.get_matching_terms(descriptions, publications)

            compared = self.get_data_available()

            r = self.get_efficiency_coeff(compared["id"])
        except TypeError:
            print("TypeError")
        return r


class ModelTableView:
    def __init__(self):
        # def __init__(self, table_object):
        db = globalDB
        # self.table_object = table_object
        # s = db.execute("SELECT models_copy.model_type_id, models_copy.contributor_type, models_copy.id, models_copy.contributor_id, models_copy.title, models_copy.description, \
        s = db.execute("SELECT models_copy.*, \
            model_types.title  as type_title, models_projects.project_id \
            FROM models_copy \
            LEFT JOIN model_types \
            ON models_copy.model_type_id=model_types.id \
            LEFT JOIN models_projects \
            ON models_copy.id=models_projects.model_id;")
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()
        # self.view["terms"] = ""
        # print self.view.columns
        # self.view = self.view[self.view["contributor_type"] == "User"]
        self.terms = 0


    def get_terms_db(self, ids):
        self.view.terms[self.view.id.isin(ids)] = self.view[self.view.id.isin(ids)].apply(
            lambda row: TermsBag().termine_service(
                row['title'] + ". " + row['description'] + " . " + str(row['type_title'])), axis=1)


class UserTableView:
    def __init__(self):
        # self.table_object = table_object
        self.db = globalDB
        s = self.db.execute("SELECT users.id, users.created_at, disciplines_people_copy.discipline_id,  \
     work_groups.institution_id, project_subscriptions.project_id, group_memberships_project_roles.project_role_id, \
     people.first_name, people.last_name, people.email, projects.name as project_name, project_roles.`name` as role \
            FROM users \
            LEFT JOIN disciplines_people_copy \
            ON disciplines_people_copy.person_id = users.person_id \
            LEFT JOIN project_subscriptions \
            ON project_subscriptions.person_id = users.person_id \
            LEFT JOIN projects \
            ON projects.id = project_subscriptions.project_id \
            LEFT JOIN group_memberships \
            ON group_memberships.person_id = users.person_id \
            LEFT JOIN work_groups \
            ON work_groups.id = group_memberships.work_group_id \
            LEFT JOIN group_memberships_project_roles \
            ON group_memberships_project_roles.group_membership_id = group_memberships.id \
            LEFT JOIN people \
            ON people.id = users.person_id \
            LEFT JOIN project_roles\
            ON project_roles.id = group_memberships_project_roles.project_role_id;")
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()
        self.view = self.view[self.view["project_id"].notnull()]
        self.view.fillna(0)
        # self.view['tenure'] =self.view.apply(lambda row:(datetime(2013,01,31) - datetime(row['created_at'])), axis=1)

    def fill_sharing_ratio(self):
        self.view["ds_ratio"] = 0.0
        self.view["ds_ratio"] = self.view.apply(lambda row: User(row["id"]).get_sharing_ratio(), axis=1)

    def fill_number_assets(self):
        self.view["no_assets"] = 0.0
        self.view["no_assets"] = self.view.apply(lambda row: User(row["id"]).get_number_assets(), axis=1)

    def fill_administrative_roles(self):
        self.view["has_pal"] = 0
        self.view["has_pal"] = self.view.apply(lambda row: User(row["id"]).has_pals(), axis=1)
        self.view["has_coor"] = 0
        self.view["has_coor"] = self.view.apply(lambda row: User(row["id"]).is_in_coordination_inst(), axis=1)

    def remove_sysmodb(self):
        project = Project(12)
        sysmobd = project.get_members()
        self.view = self.view[~self.view.id.isin(sysmobd)]

    def remove_duplicated_joins(self):
        self.view = self.view.drop_duplicates(["id", "discipline_id", "role"])
        # work_groups.institution_id,

    def reaffirm_pal(self):
        pals = self.view[self.view["project_role_id"] == 6]
        self.view.loc[self.view.id.isin(pals["id"]), 'role'] = "Sysmo-DB Pal"
        self.view.loc[self.view.id.isin(pals["id"]), 'project_role_id'] = 6

    def remove_newcollaborators(self):
        self.view = self.view[self.view["created_at"] < datetime(2010, 1, 1)]

    def cleaning_data(self):
        self.view.loc[pandas.isnull(self.view["project_role_id"]), 'role'] = "Member"
        self.view.loc[pandas.isnull(self.view["project_role_id"]), 'project_role_id'] = 1




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
    def __init__(self, id):
        self.id = int(id)
        pass

    def get_members(self):
        subs = ProjectSubsTableView()
        subscriptions = subs


        members = subscriptions.view[subscriptions.view["project_id"] == self.id]

        #Filter New Members
        members["created_at"] = pandas.to_datetime(members["created_at"])
        members = members[members["created_at"] < datetime(2013, 1, 1)]

        return members["user_id"]

    def get_sharing_ratio(self):
        b = assetsView

        # def lala(id):
        #     print id
        #     b = Asset(id["asset_id"])
        #     return b.get_permission_label("download")

        # b.assets = b.assets[b.assets["project_id"] == id]
        # b.assets['access'] = ""
        # b.assets['access'] = b.assets.apply(lambda row: lala(row), axis=1)
        grpA = b.assets.groupby('project_id')

        project = grpA.get_group(self.id)
        total = len(project)
        open = len(project[project["access"] == 'open'])
        intra = len(project[project["access"] == 'intra'])
        # partial_intra = len(project[project["access"] == 'partial_intra'])
        inter = len(project[project["access"] == 'inter'])
        ratio = (intra + open + inter ) / total
        return ratio

    def get_visibility_ratio(self):
        b = assetsView

        # def lala(id):
        #     print id
        #     b = Asset(id["asset_id"])
        #     return b.get_permission_label("view")

        # b.assets = b.assets[b.assets["project_id"] == id]
        # b.assets['access'] = ""
        # b.assets['access'] = b.assets.apply(lambda row: lala(row), axis=1)
        grpA = b.assets.groupby('project_id')
        # for i in list([1,2,3,5,6,8,9,10,11,12,14,15]):
        project = grpA.get_group(self.id)
        total = len(project)
        open = len(project[project["label"] == 'open'])
        intra = len(project[project["label"] == 'intra'])
        partial_intra = len(project[project["label"] == 'partial_intra'])
        inter = len(project[project["label"] == 'inter'])
        ratio = (intra + open + inter) / total
        return ratio

    def get_coordinator(self):
        m = self.get_members()
        users = userTableView
        mem = users.view[users.view.id.isin(m)]
        c = mem[mem["project_role_id"] == 3]
        if len(c):
            r =  c
        else:
            r = False
        return r

    def get_pals(self):
        m = self.get_members()
        users = userTableView
        mem = users.view[users.view.id.isin(m)]
        c = mem[mem["project_role_id"] == 6]
        if len(c) > 0:
            r = c
        else:
            r = False
        return r



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

    def fill_ds_ratio(self):
        self.view["ds_ratio"] = 0.0
        self.view["ds_ratio"] = self.view.apply(lambda row: Project(row['id']).get_sharing_ratio(), axis=1)



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
        df1 = model_view.view[["title", "description", "contributor_id", "type_title", "id", 'project_id', 'label', 'access', 'terms']]
        df2 = data_view.view[['title', 'description', 'contributor_id', 'id', 'project_id', 'label', 'access', 'terms']]
        df1['resource_type'] = 'Model'
        df2['resource_type'] = 'DataFile'
        self.assets = pandas.concat([df2, df1], ignore_index=True)
        self.assets['asset_id'] = range(1, len(self.assets) + 1)
        model_auth_view = TableView("model_auth_lookup")
        data_auth_view = TableView("data_file_auth_lookup")
        df1 = model_auth_view.view
        df2 = data_auth_view.view
        df1['resource_type'] = 'Model'
        df2['resource_type'] = 'DataFile'
        df1 = df1.rename(columns={'asset_id': 'id'})
        m = self.assets[self.assets["resource_type"] == "Model"]
        merge_models = pandas.DataFrame.merge(df1, m[list(['id', 'asset_id'])], how='left', on='id',
                                              left_index=True, right_index=False, sort=False,
                                              suffixes=('_x', '_y'), copy=False)
        df2 = df2.rename(columns={'asset_id': 'id'})
        m = self.assets[self.assets["resource_type"] == "DataFile"]
        merge_datafiles = pandas.DataFrame.merge(df2, m[list(['id', 'asset_id'])], how='left', on='id',
                                                 left_index=True, right_index=False, sort=True,
                                                 suffixes=('_x', '_y'), copy=False)

        self.permissions = pandas.concat([merge_datafiles, merge_models], ignore_index=True)


class User:
    def __init__(self, id):
        assert (id, int)
        self.id = id
        table = userTableView
        s = table.view[table.view["id"] == id]
        if len(s) == 1:
            self.data = (s).squeeze()
        elif len(s[s.project_id.isin([12])]) > 0:
            t = s[:1]
            self.data = t.squeeze()
        else:
            t = s[:1]
            self.data = t.squeeze()
            print "this guy in many projects"


    def get_sharing_ratio(self):
        b = assetsView
        if len(b.assets[b.assets['contributor_id'] == self.id]):
            # print self.id
            grpA = b.assets.groupby('contributor_id')
            user = grpA.get_group(self.id)
            total = len(user)
            open = len(user[user["access"] == 'open'])
            intra = len(user[user["access"] == 'intra'])
            inter = len(user[user["access"] == 'inter'])
            ratio = (intra + open + inter) / total
        else:
            ratio = 0.0

        return ratio

    def get_number_assets(self):
        b = assetsView
        if len(b.assets[b.assets['contributor_id'] == self.id]):
            r = len(b.assets[b.assets['contributor_id'] == self.id])
        else:
            r = 0.0
        return r

    def is_in_coordination_inst(self):
        c = Project((self.data['project_id'])).get_coordinator()
        if isinstance(c, pandas.DataFrame):
            d = c[c['institution_id'] == self.data['institution_id']]
            if len(d) > 0:
                r = True
            else:
                r =False
        else:
            r =False
        return r

    def has_pals(self):
        c = Project((self.data['project_id'])).get_pals()
        if isinstance(c, pandas.DataFrame):
            d = c[c['institution_id'] == self.data['institution_id']]
            if len(d) > 0:
                r = True
            else:
                r =False
        else:
         r = False

        return r

    def get_pubmed_pubs(self):
        x = PubmedSearcher()
        auths = ""
        pubs = x.get_auths_pubs(auths)
        y = x.get_authors_list(pubs)
        print y


class Asset:
    def __init__(self, id):
        self.id = id
        #
        #
        # def get_info(self):
        a = assetsView
        self.info = (a.assets[a.assets["asset_id"] == self.id]).squeeze()
        self.access = ""
        self.project = int(self.info["project_id"])
        self.permissions = a.permissions[a.permissions["asset_id"] == self.id]


        # self.info = self.info.reset_index(drop=True)
        # self.info = self.info.to_dict('records')
        # self.info = self.info.to_dict()
        # print self.info

    def get_permission_label(self, type):
        # a = AssetsView()
        # self.get_info()
        # self.permissions = a.permissions[a.permissions["asset_id"] == self.id]
        if type == "view":
            access = self.permissions[self.permissions["can_view"] == 1]
        else:
            access = self.permissions[self.permissions["can_download"] == 1]


        access = self.__remove_sysmodb_permissions(access)

        self.access = self.__is_open(access)

        if not self.access:
            self.access = self.__is_intra(access)
        if not self.access:
            self.access = self.__is_partial_intra(access)
        if not self.access:
            self.access = self.__is_private(access)
        if not self.access:
            self.access = self.__is_inter(access)
        if not self.access:
            self.access = self.__is_ext_private(access)

        # print "lolo"
        # print access


        return self.access


    @staticmethod
    def __is_open(permissions):
        r = permissions[permissions.user_id.isin([0])]
        if r.shape[0]:
            return "open"
        return ""

    @staticmethod
    def __is_private(permissions):
        if permissions.shape[0] == 1 and len(permissions[permissions["can_delete"] == 1]) > 0:
            return "private"
        return ""

    @staticmethod
    def __is_ext_private(permissions):

        # print permissions
        if len(permissions[permissions["can_delete"] == 1]) > 0:
            return "extended private"
        return ""


    def __is_intra(self, permissions):
        projects = Project(self.project)
        project_members = projects.get_members()

        if set(permissions["user_id"]).issubset(set(project_members)) and \
                        len(permissions["user_id"]) == len(project_members):
            return "intra"
        return ""

    def __is_partial_intra(self, permissions):
        projects = Project(self.project)
        project_members = projects.get_members()

        # print permissions["user_id"]
        # print project_members

        if set(permissions["user_id"]).issubset(set(project_members)) and \
            len(set(permissions["user_id"]).union(set(project_members))) > 2:
            return "partial_intra"
        return ""

    def __is_inter(self, permissions):
        projects = Project(self.project)
        project_members = projects.get_members()

        if set(permissions["user_id"]).issuperset(set(project_members)):
            return "inter"
        return ""

    def __remove_sysmodb_permissions(self, permissions):
        if self.project != 12:
            projects = Project(12)
            sysmodb_members = projects.get_members()
            permissions = permissions[~permissions.user_id.isin(sysmodb_members)]
        return permissions

    def get_terms(self):
        r = self.info.to_records()
        # print r
        terms = ""
        print r['resource_type']
        if str(r['resource_type']) == '[Model]':
            terms = TermsBag().termine_service(str(r['title'] + ". " + r['description'] + " . " + str(r['type_title'])))
        elif str(r['resource_type']) == '[DataFile]':
            terms = TermsBag().termine_service(str(r['title'] + ". " + r['description']))
        else:
            print "Missing resource ID"
        return terms


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
        self.data["terms"] = TermsBag().termine_service(
            str(self.data['title'] + ". " + self.data['description'] + " . " + str(self.data['type_title'])))
        return self.data["terms"]


class TermsBag:
    def __init__(self, text=" "):
        self.text = text
        self.terms = self.to_data_frame()

    def termine_service(self, text):
        port = termineLocator().gettermine_porttype()
        req = analyze_request()
        print ".."
        print text
        # decoded_str = text.decode('Latin1')
        # encoded_str = decoded_str.encode('ascii', 'replace')
        decoded_str = unidecode.unidecode(text)
        encoded_str = decoded_str.encode('ascii', 'replace')

        req._src = encoded_str
        res = port.analyze(req)
        self.text = res._result
        return res._result

    def __unicode__(self):
        return unicode(self.some_field) or u''

    def to_data_frame(self):
        list_terms = self.text.encode('ascii', 'ignore').split('\n')
        for j, line in enumerate(list_terms):
            title_trans = ''.join(chr(c) if chr(c).isupper() or chr(c).islower() else ' ' for c in range(256))
            list_terms[j] = line.translate(title_trans).strip()
        df_terms = pandas.DataFrame(list_terms, columns=['terms'])
        self.terms = df_terms
        return df_terms

    def compare_with(self, terms_bag):
        self.to_data_frame()
        similarly = self.terms[self.terms.terms.isin(terms_bag.terms)]
        return similarly

class MyDbTable:
    def __init__(self):
        """


        """
        self.db = MySQLdb.connect("127.0.0.1","root","","sysmo")
        self.cursor = self.db.cursor()

    def update_model_access(self, value, id):
        self.cursor.execute("""
           UPDATE models_copy
           SET access=%s
           WHERE id=%s
        """, (value, id))


    def update_model_terms(self, value, id):
        self.cursor.execute("""
           UPDATE models_copy
           SET terms=%s
           WHERE id=%s
        """, (value, id))


    def update_datafile_access(self, value, id):
        self.cursor.execute("""
           UPDATE data_files_copy
           SET access=%s
           WHERE id=%s
        """, (value, id))


    def update_datafile_terms(self, value, id):
        self.cursor.execute("""
           UPDATE data_files_copy
           SET terms=%s
           WHERE id=%s
        """, (value, id))

    def update_publications_ds_ratio(self, value, id):
        self.cursor.execute("""
           UPDATE publications_copy
           SET ds_ratio=%s
           WHERE id=%s
        """, (value, id))


    def close_con(self):
        self.db.commit()
        self.db.close()


dataTableView = DataTableView()
modelTableView = ModelTableView()
assetsView = AssetsView()
userTableView = UserTableView()
# userTableView.fill_sharing_ratio()
# userTableView.fill_number_assets()
# userTableView.fill_administrative_roles()