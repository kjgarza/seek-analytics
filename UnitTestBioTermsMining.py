from __future__ import division
from BioTermsMining import *
import pandas.tools.rplot as rplot
import matplotlib.pyplot as plt
import numpy as np

from flask import Flask, render_template
app = Flask(__name__)

db = sqlsoup.SQLSoup('mysql+mysqldb://root:@127.0.0.1/sysmo?charset=ascii')


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/permission')
def permissions():
    a = Asset(15).get_permissions()
    print(a)
    return 'PASS!'

@app.route('/test_AssetsView')
def permissions2():
    a = AssetsView()

    def lala(id):
        print id
        b = Asset(id["asset_id"])
        return b.get_permission_label("download")



    a.assets['access'] = ""
    a.assets['access'] = a.assets.apply(lambda row:lala(row), axis=1)


    return 'PASS!'
    # return render_template("analysis.html", name="lol", data=a.assets.to_html())



@app.route('/test_get_sharing_ratio')
def test_get_sharing_ratio():
    p = Publication("22607453")
    s = p.get_data_sharing_ratio()
    if s:
        return render_template("analysis.html", name='PASS!', data=s)
    else:
        r = 'FAIL!!!!!!!!!!!!!'
    return r

@app.route('/fill_sharing_ratio')
def fill_sharing_ratio():
    pbls = PublicationView()
    pbls.fill_ds_ratio()
    grouped = pbls.view.groupby('project_id')
    # print grouped.view
    print grouped['ds_ratio'].agg([np.median, np.mean, np.std])
    if isinstance(pbls, pandas.DataFrame):
        return render_template("analysis.html", name='PASS!', data=pbls.view)
    else:
        r = 'FAIL!!!!!!!!!!!!!'
    return r


@app.route('/use_stats')
def use_stats():
    u =UserTableView()
    u.fill_sharing_ratio()

    alfa = u.view.groupby('project_id')
    print alfa['ds_ratio'].agg([np.median, np.mean, np.std])
    a = u.view
    return render_template("analysis.html", name="write_access", data=a.to_html())



@app.route('/assets')
def assets_test():
    b = AssetsView()

    # b.assets = b.assets[1:30]

    def lala(id):
        print id
        b = Asset(id["asset_id"])
        return b.get_permission_label("download")

    b.assets['access'] = ""
    b.assets['access'] = b.assets.apply(lambda row:lala(row), axis=1)

    # r = b.assets.groupby(['project_id','label']).agg([len])


    grpA  = b.assets.groupby('project_id')


    for i in list([1,2,3,5,6,8,9,10,11,12,14,15]):
    # for i in list([1,2,3,5,8,14]):
        project = grpA.get_group(i)
        total = len(project)
        open = len(project[project["access"] == 'open'])
        intra = len(project[project["access"] == 'intra'])
        inter = len(project[project["access"] == 'inter'])
        ratio = (intra+open+inter)/total
        # print i+": "
        print ratio

    return 'PASS!'


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







# n, min_max, mean, var, skew, kurt = stats.describe(ll)

    # c.plot(kind="bar");
    #
    #
    # import matplotlib.pyplot as plt
    # plt.figure()

#
# # c=AssetsView()
# # print c.assets[c.assets["resource_type"] == "Model"]
# # print c.assets[c.assets["resource_type"] == "DataFile"]
# #
# # a = Asset(1003)
# # # print a.get_project()
# # # a.get_terms()
# # # print a.data
# # print a.get_permission_label()
#
# # d = range(1, len(b.assets)+1)
# #
# #
# # # print b.assets
# #
#
# b.assets = b.assets[1:30]
#
# def lala(id):
#     print id
#     b = Asset(id["asset_id"])
#     return b.get_permission_label()
#
# b.assets['label'] = ""
# b.assets['label'] = b.assets.apply(lambda row:lala(row), axis=1)
#
# print b.assets
#
# c = b.assets.groupby(['label', 'project_id'])
#
# print b.assets.groupby(['project_id','label']).agg([len])
#
# c.plot(kind="bar");
#
# #
# # print b.assets
#
# # print Asset(577).get_permission_label()
# # print Asset(222).get_permission_label()
# # print Asset(123).get_permission_label()
# # print Asset(577).get_permission_label()
# # print Asset(1009).get_permission_label()
# # print Asset(1023).get_permission_label()
# # print Asset(345).get_permission_label()
# # print Asset(66).get_permission_label()
# # print Asset(1021).get_permission_label()
#
# # if __name__ == '__main__':
# #     main("21231375")
#
# from __future__ import division
# intra = ss.query('label == "intra"')["title"]
# inter = ss.query('label == "inter"')["title"]
# open = ss.query('label == "open"')["title"]
#
# shared = intra + inter + open
# x = ss["title"]
# total = sum(x['len'])
#
# ratio = (shared)/(total)
#
# print ratio
#
