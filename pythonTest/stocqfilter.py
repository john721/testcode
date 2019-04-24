#!/usr/bin/python
# coding=utf-8
import requests
from io import StringIO
import pandas as pd
import numpy as np
import codecs
import time

datestr = '20190415'
def get_html_dfs(stryear, strmonth):
    year = int(stryear)
    month = int(strmonth)
    monthly_file = "./" + stryear + "_" + strmonth + ".html"
    try:
        with open (monthly_file, 'r') as mf:
            dfs = pd.read_html(monthly_file, encoding='utf-8')
            print ("read html file successfully")
            return dfs
    except Exception as e:
        print(e)
        if year > 1990:
    	    year -= 1911
    
        url = 'http://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'_0.html'
        if year <= 98:
        	url = 'http://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'.html'
    
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    
        r = requests.get(url, headers=headers)
        r.encoding = 'big5'
        print ("fetch html file successfully")
    
        with codecs.open( monthly_file, mode='wb') as writefile:
            writefile.write(r.text.encode('utf8'))
        dfs = pd.read_html(StringIO(r.text), encoding='big-5')
        return dfs

def monthly_report(year, month):
    dfs = get_html_dfs(year, month)
    #print dfs[1].describe

    df = pd.concat([df for df in dfs if df.shape[1] <= 11 and df.shape[1] > 5])
    
    if 'levels' in dir(df.columns):
    	df.columns = df.columns.get_level_values(1)
    else:
    	df = df[list(range(0,10))]
    	column_index = df.index[(df[0] == '公司代號')][0]
    	df.columns = df.iloc[column_index]

    df.columns = ["ID", "name", "income", "LMin", "LYMin", "MOM%", "YOY%", "ACC", "LYAcc", "%AccYoY", "remark"]
    df['income'] = pd.to_numeric(df['income'], 'coerce')
    df = df[~df['income'].isnull()]
    df = df[df['ID'] != '合計']

    fake_fin_report = ['2489']
    major_job_ng = ['2363', '3018']

    blacklist = fake_fin_report
    blacklist += major_job_ng

    df = df[df['MOM%'] > 100]
    df = df[df['YOY%'] > 10]
    df = df[df['%AccYoY'] > 10.0]
    df = df[df['ID'].isin(blacklist) == False]
    #print ("df.columns")
    #print (df.columns)
    print (df.iloc[0:25, [0,2,3,4,5,6,7,8,9,1]])
    print (df.iloc[26:50, [0,2,3,4,5,6,7,8,9,1]])
    return df

def daily_report(datestr):
    r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')
    with codecs.open( datestr + ".txt", mode='w') as writefile:
        writefile.write(r.text.encode('utf8'))

    df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
                                     for i in r.text.split('\n') 
                                     if len(i.split('",')) == 17 and i[0] != '='])), header=0)
    gt3 = df[pd.to_numeric(df['本益比'], errors='coerce') > 3]
    gt3lt10 = gt3[pd.to_numeric(df['本益比'], errors='coerce') < 10]
    print (gt3lt10)

monthly_report("108", "3")

