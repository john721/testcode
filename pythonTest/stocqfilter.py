#!/usr/bin/python
# coding=utf-8
import requests
from io import StringIO
import pandas as pd
import numpy as np
import codecs
import datetime
import time
import sys

# TODO: 找出今年配息, 殖利率等相關資訊
def get_html_dfs(stryear, strmonth):
    year = int(stryear)
    month = int(strmonth)
    monthly_file = "./mon_" + stryear + "_" + strmonth + ".html"
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
    wlist = ['8926', '2535', '3705', '2439', '2634', '6201', '2375']
    wdf = df[df['ID'].isin(wlist) == True]
    print ("White List_________\n")
    print (wdf.iloc[0:25, [0,2,3,4,5,6,7,8,9,1]])
    print ("\n")

    df = df[df['MOM%'] > 3]
    df = df[df['YOY%'] > 3]
    df = df[df['%AccYoY'] > 3.0]
    df = df[df['ID'].isin(blacklist) == False]
    df = df.sort_values(['%AccYoY'])
    #print ("df.columns")
    #print (df.columns)
    print ("Month Good_________\n")
    print (df.iloc[0:25, [0,2,3,4,5,6,7,8,9,1]])
    print (df.iloc[26:50, [0,2,3,4,5,6,7,8,9,1]])
    print (df.iloc[51:75, [0,2,3,4,5,6,7,8,9,1]])
    return df

def get_html_dfs_fin_stat(year, season, type):
    fin_stat_file = "./fin" + str(year) + "_" + str(season) + ".html"
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
    majordf.columns =         ["ID", "income", "Costs", "NetGross", "fees", "OpPft", "NetProf", "OCI", "CI", "EPS", "name"]

    # Gross Profit Margin
    majordf['gpm'] = (majordf.income - majordf.Costs)/majordf.income * 100
    cols = majordf.columns.tolist()
    cols = cols[0:3] + cols[-1:] + cols[3:-1]
    print(cols)
    majordf = majordf[cols]

    #majordf = majordf[majordf['EPS'] > 0.0]
    majordf = majordf[majordf['gpm'] > 5.0]
    white_list = monthly_report("108", "4")
    majordf = majordf.loc[majordf['ID'].isin(white_list['ID'])]

    # digit print format: 1,234,567
    for col in ['income', 'Costs','OpPft', 'NetProf', 'CI']:
        majordf[col] = majordf.apply(lambda x: "{:,}".format(x[col]), axis=1)
    print ("\n" + str(year) + " season" + str(season) + "_________")
    #print(majordf[:10])
    print(majordf)
    return

def daily_report(datestr):
    r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')
    #with codecs.open( datestr + ".txt", mode='w') as writefile:
    #    writefile.write(r.text.encode('utf8'))

    df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
                                     for i in r.text.split('\n') 
                                     if len(i.split('",')) == 17 and i[0] != '='])), header=0)
    gt3 = df[pd.to_numeric(df['本益比'], errors='coerce') > 3]
    gt3lt10 = gt3[pd.to_numeric(df['本益比'], errors='coerce') < 10]
    print (gt3lt10)

if __name__ == '__main__':
    #datestr = '20190415'
    now = datetime.datetime.now()
    datestr = str(now.year) + str(now.month) + str(now.day-1)
    #daily_report(datestr)
    if ("mon" == sys.argv[1]):
        monthly_report("108", "4")
    elif ("fin" == sys.argv[1]):
        try:
            financial_statement(107, 4)
            financial_statement(108, 1)
        except Exception as e:
            print(e)

