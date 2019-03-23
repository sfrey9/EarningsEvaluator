import os
import time
from bs4 import BeautifulSoup as bs
from urllib import request
import yaml
from easydict import EasyDict as edict
from functools import reduce
import timeit

def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r') as cfgfile:
            try:
                return edict(yaml.load(cfgfile, Loader=yaml.FullLoader))
            except yaml.YAMLError as exc:
                print(exc)
                return None
    else:
        raise Exception("The config path doesn't exist.")

def retrieve_html(datelist, path, name):
    htmldict = {}
    if name == 'yahoo':
        for date in datelist:
            url = r"{0}day={1}".format(path, date)
            with request.urlopen(url) as response:
                htmldict[date] = response.read()
    return htmldict

def switch_func(bs4element):
    if len(bs4element) == 3:
        return bs4element[1]
    elif len(bs4element) == 1:
        return bs4element[0].contents[0]
    else:
        raise Exception("The bs4 element is an unrecognized length.")

def floatify(string):
    try:
        return float(string)
    except ValueError:
        return None

def parse_table(html, date=None):
    Tbl = []
    soup = bs(html, features="html.parser")
    rows = soup.find(id="cal-res-table").find_all(class_="simpTblRow")
    for row in rows:
        rowdict = {}
        rowdict['EarningsDate'] = date
        rowdict['Symbol'] = str(row.find(attrs={"aria-label":"Symbol"}).contents[0].contents[0])
        rowdict['Company'] = str(row.find(attrs={"aria-label":"Company"}).contents[1])
        rowdict['CallTime'] = str(switch_func(row.find(attrs={"aria-label":"Earnings Call Time"}).contents))
        rowdict['EPSEstimate'] = floatify(switch_func(row.find(attrs={"aria-label":"EPS Estimate"}).contents))
        rowdict['ReportedEPS'] = floatify(switch_func(row.find(attrs={"aria-label":"Reported EPS"}).contents))
        rowdict['Surprise'] = floatify(row.find(attrs={"aria-label":"Surprise(%)"}).contents[0].contents[0])
        Tbl.append(rowdict)
    return Tbl

def main():
    cfg = load_config("config.yaml")
    datelist = ['2019-03-20','2019-03-21','2019-03-22']
    htmldict = retrieve_html(datelist=datelist, path=cfg.listing.target.BASE_URL, name=cfg.listing.target.NAME)
    Tbl = reduce((lambda x,y : x+y),[parse_table(html=v, date=k) for k,v in htmldict.items()])
    return Tbl
    
if __name__ == "__main__":
    main()

