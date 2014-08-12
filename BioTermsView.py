from BioTermsMining import *
import pandas.tools.rplot as rplot
import matplotlib.pyplot as plt
import numpy as np
from ggplot import *

from flask import Flask, render_template
app = Flask(__name__)

db = sqlsoup.SQLSoup('mysql+mysqldb://root:@127.0.0.1/sysmo?charset=ascii')


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/efficiency')
def batch_efficiency():
    # myset = [97, 8, 113, 149, 175, 176, 112, 84, 162, 186, 94, 148, 61, 102, 105, 183, 111, 127, 133, 182, 128, 132,
    # 181, 184, 103, 131, 104, 108, 143, 110, 106, 130, 107, 190, 100, 185, 206]
    myset = [34, 98, 134, 35, 136, 149, 176, 175, 174, 179, 93, 146, 142, 87]
    # myset = [97]
    s = db.execute("SELECT * FROM publications WHERE pubmed_id IS NOT NULL")
    publications = pandas.DataFrame(s.fetchall())
    publications.columns = s.keys()
    s = publications[publications.id.isin(myset)]
    # a = BioTermsMining()
    # a = Publication()
    stas_tbl = pandas.DataFrame(columns=['pubmed_id', 'recall', 'precision'])
    for index, row in s.iterrows():
        print str(int(row['pubmed_id']))
        if None != row['pubmed_id']:
            a = Publication(str(int(row['pubmed_id'])))
            stas = a.get_recall()
            print stas
            # stas = a.get_recall(str(int(row['pubmed_id'])))
            try:
                stas_tbl = stas_tbl.append(stas, ignore_index=True)
            except AttributeError:
                print("AttributeError")
    avg_recall = reduce(lambda x, y: x + y, stas_tbl["recall"]) / len(stas_tbl["recall"])
    avg_precision = reduce(lambda x, y: x + y, stas_tbl["precision"]) / len(stas_tbl["precision"])
    print stas_tbl.append([{'pubmed_id': 'AVG', 'recall': avg_recall, 'precision': avg_precision}], ignore_index=True)
    return 'PASS!'

@app.route('/wo_isa')
def get_twenty_wo_isa():
    r = pandas.DataFrame()
    x = pandas.DataFrame()
    # r['ids'] = [19321498, 18395130, 20412803, 20214910, 17725564, 18491319, 18546160, 19047653, 19193632,19403106, 19374982, 21133689, 22281772, 18086213, 21219666, 20947526, 21479178, 22096228,23175651, 22052476]
    r['ids'] = [19095699,18937253,19933161,20197501,17822389,20502716,18208493,18628769,18952880,18474306,20389117,19403106,20726779,22038603,22281772,21074401,21947264,23136871]
    # r['ids'] = [20238180,19688348,20739311,20617312,21252224,22325620,21212688,22511268,22607453,22686585,22712534,22870390,23332010]
    r["abstract"] = ""
    p = Publication()
    models_table = ModelTableView(db.models)
    # models_table = DataTableView(db.data_files)

    def lala(contributor_id):
        assets = models_table.view[models_table.view.contributor_id == contributor_id]

        if assets.shape[0] == 0:
            print "No assets"
        # lo = str("Title: " + assets['title'] + assets['description'])
        for index, row in assets.iterrows():
            print " "
            print str("> __id:__ " + str(int(row['id'])))
            print " "
            print str("> __Contr:__ " + str(int(row['contributor_id'])))
            print " "
            print str("> __Title:__ " + row['title'])
            print " "
            print str("> __Description:__ " + row['description'])
            print " "
            print "------"
        # return lo

    def xsols(pubmed_id):
        handle = efetch(db='pubmed', id=str(pubmed_id), retmode='text', rettype='abstract', email='garzaguk@.cs.man.ac.uk')
        text = handle.read()
        return text

    for index, row in r.iterrows():
        handle = efetch(db='pubmed', id=str(row['ids']), retmode='text', rettype='abstract', email='garzaguk@.cs.man.ac.uk')
        text = handle.read()
        # row.ix["abstract"] = text
        print " "
        print "###Publication:"
        print text

        user_ids = p.get_authors(str(row['ids']))
        r["desc"] = user_ids.apply(lambda line: lala(line))
        print " "
        print "------"


    # r["abstract"] = r['ids'].apply(lambda line: xsols(line))

    # return render_template("wo_isa.html", name="sasa", data=r.to_html(classes='list'))
    return 'PASS!'

@app.route('/permission')
def permissions():
    a = Asset(15).get_permissions()
    print(a)
    return 'PASS!'

@app.route('/write_access/<resource_type>')
def write_label(resource_type):
    a = AssetsView()
    def lala(id):
        print id
        b = Asset(id["asset_id"])
        return b.get_permission_label("download")

    a.assets = a.assets[a.assets['resource_type'] == resource_type]
    a.assets['access'] = a.assets.apply(lambda row:lala(row), axis=1)
    dt = MyDbTable()

    if resource_type == 'Model':
        a.assets.apply(lambda row: dt.update_model_access(row['access'], row['id']), axis=1)
    if resource_type == 'DataFile':
        a.assets.apply(lambda row: dt.update_datafile_access(row['access'], row['id']), axis=1)
    dt.close_con()
    return render_template("analysis.html", name="write_access", data=a.assets.to_html())

@app.route('/write_terms')
def write_terms():
    a = AssetsView()

    def lala(id):
        print id
        b = Asset(id["asset_id"])
        return b.get_terms()


    a.assets = a.assets[900:]

    a.assets = a.assets[a.assets['resource_type'] == 'Model']


    a.assets['terms'] = ""
    a.assets['terms'] = a.assets.apply(lambda row:lala(row), axis=1)


    dt = MyDbTable()
    a.assets.apply(lambda row: dt.update(row['terms'], row['id']), axis=1)

    dt.close_con()

    return 'PASS!'


@app.route('/write_ds_ratio')
def write_ds_ratio():
    """
    Writes Data Sharing Ratio into publication_copy table

    :return:
    """
    u =PublicationView()
    u.fill_ds_ratio()

    print "Got Data"

    dt = MyDbTable()
    u.view.apply(lambda row: dt.update_publications_ds_ratio(row['ds_ratio'], row['id']), axis=1)
    dt.close_con()
    return render_template("analysis.html", name="write_access", data=u.view.to_html())



@app.route('/projects_ds_sharing')
def projects_ds_sharing():
    u = PublicationView()

    gr = u.view.groupby('project_id')
    print gr['ds_ratio'].agg([np.median, np.mean, np.std])
    return render_template("analysis.html", name="write_access", data=u.view.to_html())

@app.route('/users_ds_sharing')
def users_ds_sharing():
    p = PublicationView()
    u = userTableView
    table = pandas.DataFrame(columns=['id', 'pubmed_id',"ds_ratio"])

    u.remove_sysmodb()
    u.reaffirm_pal()
    u.remove_duplicated_joins()
    u.cleaning_data()
    u.fill_sharing_ratio()
    u.fill_number_assets()
    u.fill_administrative_roles()



    u.view['ds_ratio'] = 0

    for i, row in p.view.iterrows():
        auths = pandas.DataFrame(columns=['id', 'pubmed_id',"ds_ratio"])
        x = Publication(str(int(row['pubmed_id'])))
        auths["id"] = x.get_authors()
        auths["pubmed_id"] = str(int(row['pubmed_id']))
        auths["ds_ratio"] = float(row['ds_ratio'])
        table = pandas.concat([table, auths], ignore_index=True)

    table[['ds_ratio']] = table[['ds_ratio']].astype(float)
    gr = table.groupby('id')

    x =  gr['ds_ratio'].aggregate([np.mean, np.sum])

    user_ds = pandas.DataFrame.merge(u.view, x, how='left', left_on='id',
                                        right_index=True, sort=False,
                                        suffixes=('_x', '_y'), copy=True)
    print x

    user_ds.to_csv("users_data", sep=',', encoding='utf-8')


    return render_template("analysis.html", name="write_access", data=user_ds.to_html())




@app.route('/interviewees_check')
def interviewees_check():
    interv_id = [15, 233]

    # for row in range(1,9):
    #     r = Project(row)
    #     e = r.get_pals()
    #     print e["first_name"]

    #
    # f = User(11)
    # print f.data
    # print f.has_pals()
    # # print f.is_in_coordination_inst()
    #



    user_data = userTableView
    user_data.remove_sysmodb()
    user_data.reaffirm_pal()
    user_data.remove_duplicated_joins()
    user_data.cleaning_data()
    user_data.fill_sharing_ratio()
    user_data.fill_number_assets()
    user_data.fill_administrative_roles()

    print user_data

    l = user_data.view.sort(['project_name', 'ds_ratio', 'no_assets'])

    l.to_csv("users_data", sep=',', encoding='utf-8')

    return render_template("analysis.html", name="write_access", data=l.to_html())


@app.route('/interviewees_check2')
def interviewees_check2():
    #interv_id = [15, 223, 28, 97, 13, 215, 241, 12, 55,17]
    interv_id = [15, 223, 28, 97, 13, 215, 241, 12, 55, 17, 193, 88]

    # mazs 15
    # afsa 28
    # michael 97
    # martij 13
    # lajeandro 223
    # abeer 215
    # arazz 241
    # mark 12
    # peter 193
    # ulf 88
    # sarah 55
    # Lief 17

    user_data = userTableView
    user_data.view = user_data.view[user_data.view.id.isin(interv_id)]
    user_data.remove_sysmodb()
    user_data.reaffirm_pal()
    user_data.remove_duplicated_joins()
    user_data.cleaning_data()
    user_data.fill_sharing_ratio()
    user_data.fill_number_assets()
    user_data.fill_administrative_roles()

    print user_data

    user_data.view = user_data.view.drop_duplicates("email")

    grpP = user_data.view.groupby("project_id")
    print grpP['id'].agg([np.count_nonzero])

    grpD = user_data.view.groupby("discipline_id")
    print grpD['id'].agg([np.count_nonzero])


    l = user_data.view.sort(['project_name', 'role', 'ds_ratio', 'no_assets'])

    l.to_csv("users_data", sep=',', encoding='utf-8')

    return render_template("analysis.html", name="write_access", data=l.to_html())




@app.route('/test_get_sharing_ratio')
def test_get_sharing_ratio():
    p = Publication("22607453")
    if p.get_data_sharing_ratio():
        r = 'PASS!'
    else:
        r = 'FAIL!!!!!!!!!!!!!'
    return r

@app.route('/test_get_sharing_ratio2')
def test_get_sharing_ratio2():
    ps = ProjectTableView()

    for i in list([1,2,3,5,8,14]):
        x =  Project(i).get_sharing_ratio()
        print i
        print x

    # ps.view["ratio"] = ps.view.apply(lambda row: Project(row['id']).get_sharing_ratio(), axis=1)
    return x
    # return render_template("analysis.html", name="write_access", data=ps.view.to_html())


@app.route('/fill_sharing_ratio')
def fill_sharing_ratio():
    pbls = PublicationView()
    pbls.fill_ds_ratio()
    grouped = pbls.groupby('project_id')
    print grouped['ds_ratio'].agg([np.sum, np.mean, np.std])

    if isinstance(pbls, pandas.DataFrame):
        r = 'PASS!'
    else:
        r = 'FAIL!!!!!!!!!!!!!'
    return r


@app.route('/updates_dates')
def updates_dates():
    m = DataTableView()
    eval10 = datetime(2010,05,01)  # http://www.bbsrc.ac.uk/pa/grants/AwardDetails.aspx?FundingReference=BB%2FI004637%2F1
    eval11 = datetime(2011,02,01)
    eval12 = datetime(2012,05,01)  # https://seek.sysmo-db.org/presentations/38
    eval13 = datetime(2013,03,01)  # https://seek.sysmo-db.org/presentations/85
    print m.view

    def hongo(up, cr):
        r = True
        print up.date()
        if up.date() == cr.date():
            r = False
        return r


    m.view['updated'] = m.view.apply(lambda row: hongo(row['updated_at'], row['created_at'] ), axis=1)
    m.view['fecha'] = m.view.apply(lambda row: row['created_at'].toordinal(), axis=1)
    # f = m.view.groupby(m.view.updated_at).size().reset_index(name='qty')




    ll = ggplot(m.view, aes(x='fecha',fill='updated'))+ geom_histogram()   + \
         scale_x_date(breaks=date_breaks('1 month'), labels='%b %Y') + \
         geom_vline(xintercept = eval10.toordinal(), linetype='solid') + \
         geom_vline(xintercept = eval11.toordinal(), linetype='solid') + \
         geom_vline(xintercept = eval12.toordinal(), linetype='solid') + \
         geom_vline(xintercept = eval13.toordinal(), linetype='solid')
    print ll

    # sp = ggplot(m.view, aes(x='created_at', y='updated_at', group='contributor_type', color='contributor_type'))  #+ geom_bar(stat="identity") + \
    #geom_vline(xintercept = (eval11), linetype=5) + geom_vline(xintercept = (eval12), linetype=5) + geom_vline(xintercept = (eval13), linetype=5)
    # print sp

    return True


@app.route('/export_df')
def export_df():
    df = userTableView
    df.view.to_csv("users_data", sep=',', encoding='utf-8')


@app.route('/project_mem_numbers')
def project_mem_numbers():
    p = UserTableView()
    # print p.view
    # x = p.view.groupby('project_id').id.nunique()
    # print x
    # # x = p.view.groupby('project_id').size()
    # # print x

    p.remove_sysmodb()
    p.remove_newcollaborators()

    x = p.view.groupby('project_id').id.nunique()
    print x


    return render_template("analysis.html", name="write_access", data=p.view.to_html())


if __name__ == '__main__':
    app.run(debug=True)





if __name__ == '__main__':
    app.run(debug=True)



# get_twenty_wo_isa()

# c = AssetsView()
# print(c.assets)








#
#
# b = Publication()
# b.get_used_items("22686585")
# b.get_data_sharing_ratio("22686585")

# s.apply(lambda row: a.get_recall_pubmed_id(row['pubmed_id']), axis=1)


# batch_efficiency()

#
# a = Publication()
# a.get_recall("22686585", a.get_data_sharing_ratio("22686585")["id"])

# a = BioTermsMining()


# a.get_recall_pubmed_ids(["21252224","21252224"])
# a.get_recall_pubmed_id("22686585")
# ## a.get_recall_pubmed_id("20053288")
# a.get_recall_pubmed_id("21097579")
# a.get_recall_pubmed_id("21252224")
# # # a.get_recall_pubmed_id("21106498")
# a.get_recall_pubmed_id("19802714")
# # # a.get_recall_pubmed_id("21815947")
# a.get_recall_pubmed_id("22712534")
# a.get_recall_pubmed_id("22511268")
# a.get_recall_pubmed_id("22923596")
# a.get_recall_pubmed_id("23332010")

# a.get_recall("21252224",pandas.DataFrame([54,88,1076]))
# s = a.termine_service(
#     "Alkaline phosphatase is normally localized to the periplasm of Escherichia coli and is unable to fold into its native conformation if retained in the cytoplasm of growing cells. The alkaline phosphatase activity of E. coli expressing a version of the protein without a signal sequence was nonetheless found to increase gradually when the growth of cells was suspended. At least 30% of the ")
#
# print(pandas.DataFrame.from_records(s))

# print(pandas.DataFrame(s, columns=["p", "term"]))
# print(type(s))
# s2= s.encode('ascii','ignore')
# print(type(s2))
# splits = s2.split('\n')
# print(splits)
#
# for i, row in enumerate(splits):
#     title_trans=''.join(chr(c) if chr(c).isupper() or chr(c).islower() else ' ' for c in range(256))
#     # la = ''.join([i for i in row if not i.isdigit()])
#     # print(row.translate(title_trans).strip())
#     splits[i] = row.translate(title_trans).strip()
# print(splits)



# terms = [w.split('\n', 2)[1] for w in words]


# main(a, "21252224")