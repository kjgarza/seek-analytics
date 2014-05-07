
class Asset:
    def __init__(self, id):


    def get_info(self):
        a = AssetsView()
        self.info = a.assets[a.assets["id"] == self.id]

    def get_permission_label(self):
        a = AssetsView()
        self.permissions = a.permissions[a.permissions["asset_id"] == self.id]
        # permissions = AssetsView.permissions[AssetsView.permissions["asset_id"] == self.info.id]
        access = self.permissions[self.permissions["can_download"] == 1]
        self.info["access"] = self.is_open(access)
        self.info["access"] = self.is_private(access)
        self.info["access"] = self.is_intra(access)
        self.info["access"] = self.is_partial_intra(access)
        self.info["access"] = self.is_inter(access)
        return self.info["access"]

    @staticmethod
    def is_open(permissions):
        r = permissions[permissions.user_id.isin([0])]
        if r.shape[0]:
            return "open"

    @staticmethod
    def is_private(permissions):
        if permissions.shape[0] == 1 and \
                permissions[permissions["can_delete"] == 1]:
            return "private"

    def is_intra(self, permissions):
        projects = ProjectTableView()
        project_members = projects.get_members(self.info["project_id"])

        if set(permissions["user_id"]).issubset( set(project_members) ) and \
                len(permissions["user_id"]) == len(project_members):
            return "intra"

    def is_partial_intra(self, permissions):
        project_members = ProjectTableView.get_members(self.info["project_id"])

        if set(permissions["user_id"]).issubset( set(project_members) ):
            return "partial_intra"

    def is_inter(self, permissions):
        project_members = ProjectTableView.get_members(self.info["project_id"])

        if set(permissions["user_id"]).issuperset( set(project_members) ):
            return "inter"

class TableView:
    def __init__(self, table_name):
        self.db = sqlsoup.SQLSoup('mysql+mysqldb://root:@127.0.0.1/sysmo?charset=ascii')
        s = self.db.execute("SELECT * FROM " + table_name)
        self.view = pandas.DataFrame(s.fetchall())
        self.view.columns = s.keys()

class Model(Asset):
    def __init__(self, id):
        table = TableView("models")
        self.data = table[table["id"] == id]

    def get_project(self):
        m = TableView("models_projects")
        self.data["project_id"] = m.view[m.view["model_id"] == self.id]
        return self.data["project_id"]

    def get_asset_id(self):
        m = TableView("assets")
        m = m.view[m.view["resource_type"] == "model"]
        self.data["asset_id"] = m.view[m.view["resource_id"] == self.id]
        return self.data["asset_id"]


__author__ = 'kristian'
