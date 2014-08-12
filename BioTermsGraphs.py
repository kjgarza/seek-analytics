__author__ = 'kristian'
from BioTermsMining import *
import pandas.tools.rplot as rplot
import matplotlib.pyplot as plt
import numpy as np
from ggplot import *

db = sqlsoup.SQLSoup('mysql+mysqldb://root:@127.0.0.1/sysmo?charset=ascii')


def updates_dates():
    m = ModelTableView()
    eval10 = datetime(2010,05,01)  # http://www.bbsrc.ac.uk/pa/grants/AwardDetails.aspx?FundingReference=BB%2FI004637%2F1
    eval11 = datetime(2011,02,01)
    eval12 = datetime(2012,05,01)  # https://seek.sysmo-db.org/presentations/38
    eval13 = datetime(2013,03,01)  # https://seek.sysmo-db.org/presentations/85

    def hongo(up, cr):
        r = True
        print up.date()
        if up.date() == cr.date():
            r = False
        return r

    m.view['updated'] = m.view.apply(lambda row: hongo(row['updated_at'], row['created_at'] ), axis=1)
    m.view['fecha'] = m.view.apply(lambda row: row['updated_at'].toordinal(), axis=1)
    ll = ggplot(m.view, aes(x='fecha',fill='updated'))+ geom_histogram()   + \
         scale_x_date(breaks=date_breaks('3 month'), labels='%b %Y') + \
         geom_vline(xintercept = eval10.toordinal(), linetype='solid') + \
         geom_vline(xintercept = eval11.toordinal(), linetype='solid') + \
         geom_vline(xintercept = eval12.toordinal(), linetype='solid') + \
         geom_vline(xintercept = eval13.toordinal(), linetype='solid')
    print ll


# updates_dates()


def view_activity():

    m = TableView("activity_logs")

    eval10 = datetime(2010,05,01)  # http://www.bbsrc.ac.uk/pa/grants/AwardDetails.aspx?FundingReference=BB%2FI004637%2F1
    eval11 = datetime(2011,02,01)
    eval12 = datetime(2012,05,01)  # https://seek.sysmo-db.org/presentations/38
    eval13 = datetime(2013,03,01)  # https://seek.sysmo-db.org/presentations/85

    ds =m.view[m.view['action'] == 'show']
    # ds =ds[(ds['activity_loggable_type'] == 'Person')]
    ds =ds[ds.activity_loggable_type.isin(["Model", "DataFile","Person"])]
    ds =ds[ds['culprit_type'] == 'User']
    ds['date'] = ds.apply(lambda row: row['updated_at'].toordinal(), axis=1)
    # ds =m.view[m.view['activity'] == 'show']



    sp = ggplot(ds, aes(x='date', fill='culprit_type'))  + \
        geom_histogram() + \
        geom_density() + \
        scale_x_date(breaks=date_breaks('3 months'), labels='%b %Y') + \
        facet_grid('activity_loggable_type')  + \
        geom_vline(xintercept = eval10.toordinal(), linetype='solid') + \
        geom_vline(xintercept = eval11.toordinal(), linetype='solid') + \
        geom_vline(xintercept = eval12.toordinal(), linetype='solid') + \
        geom_vline(xintercept = eval13.toordinal(), linetype='solid')
        # ylim(0, 1000) + \

    print sp

def view_activity_user():

    m = TableView("activity_logs")
    ds =m.view[m.view['culprit_type'] == 'User']
    ds['date'] = ds.apply(lambda row: row['updated_at'].toordinal(), axis=1)
    # ds =m.view[m.view['activity'] == 'show']

    sp = ggplot(ds, aes(x='culprit_id', fill='action'))  + \
        geom_histogram() + \
        facet_grid('activity_loggable_type')
    print sp


view_activity()