#!/usr/bin/python
# coding=utf-8
import requests
from io import StringIO
import pandas as pd
import numpy as np
import codecs
import time

# TODO: 找出今年配息, 殖利率等相關資訊
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

def get_html_dfs_fin_stat(year, season, type):
    fin_stat_file = "./" + str(year) + "_" + str(season) + ".html"
    try:
        with open (fin_stat_file, 'r') as fsf:
            dfs = pd.read_html(fin_stat_file, encoding='utf-8')
            print ("read html file successfully")
            return dfs
    except Exception as e:
        print(e)
        if year >= 1000:
            year -= 1911
            
        if type == '綜合損益彙總表':
            url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb04'
        elif type == '資產負債彙總表':
            url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb05'
        elif type == '營益分析彙總表':
            url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb06'
        else:
            print('type does not match')

        r = requests.post(url, {
            'encodeURIComponent':1,
            'step':1,
            'firstin':1,
            'off':1,
            'TYPEK':'sii',
            'year':str(year),
            'season':str(season),
        })

        r.encoding = 'utf8'
        dfs = pd.read_html(r.text)
        print ("fetch html file successfully")

        with codecs.open( fin_stat_file, mode='wb') as writefile:
            writefile.write(r.text.encode('utf8'))
        dfs = pd.read_html(StringIO(r.text), encoding='big-5')

        return dfs


# source:https://www.finlab.tw/Python-%E8%B2%A1%E5%A0%B1%E7%88%AC%E8%9F%B2-1-%E7%B6%9C%E5%90%88%E6%90%8D%E7%9B%8A%E8%A1%A8/
def financial_statement(year, season, type='綜合損益彙總表'):
    dfs = get_html_dfs_fin_stat(year, season, type)
    # 3rd df is the major table
    majordf = dfs[3]
    majordf = majordf.iloc[:, [0,    2,        3,       5,           10,     12,        19,         20,    22,   29,   1     ] ]
    majordf.columns =         ["ID", "income", "Costs", "net gross", "fees", "op. pft", "NetProf", "OCI", "CI", "EPS", "name"]
    print(majordf)
    return

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

#monthly_report("108", "3")
financial_statement(107, 1)

