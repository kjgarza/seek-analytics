from BioTermsMining import *
import pandas.tools.rplot as rplot
import matplotlib.pyplot as plt

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

@app.route('/write_label')
def write_label():
    a = AssetsView()

    def lala(id):
        print id
        b = Asset(id["asset_id"])
        return b.get_permission_label()



    a.assets['label'] = ""
    a.assets['label'] = a.assets.apply(lambda row:lala(row), axis=1)

    a.assets = a.assets[a.assets['resource_type'] == 'Model']

    dt = MyDbTable()
    a.assets.apply(lambda row: dt.update(row['label'], row['id']), axis=1)

    dt.close_con()

    return 'PASS!'
    # return render_template("analysis.html", name="lol", data=a.assets.to_html())

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


@app.route('/test_get_sharing_ratio')
def test_get_sharing_ratio():
    p = Publication("22607453")
    if p.get_data_sharing_ratio():
        r = 'PASS!'
    else:
        r = 'FAIL!!!!!!!!!!!!!'
    return r

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