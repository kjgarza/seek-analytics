from BioTermsMining import *
from __future__ import division

b = AssetsView()

# b.assets = b.assets[1:30]

def lala(id):
    print id
    b = Asset(id["asset_id"])
    return b.get_permission_label()

b.assets['label'] = ""
b.assets['label'] = b.assets.apply(lambda row:lala(row), axis=1)

# r = b.assets.groupby(['project_id','label']).agg([len])


grpA  = b.assets.groupby('project_id')


for i in list([1,2,3,5,6,8,9,10,11,12,14,15]):
# for i in list([1,2,3,5,8,14]):
    project = grpA.get_group(i)
    total = len(project)
    open = len(project[project["label"] == 'open'])
    intra = len(project[project["label"] == 'intra'])
    inter = len(project[project["label"] == 'inter'])
    ratio = (intra+open+inter)/total
    # print i+": "
    print ratio



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
