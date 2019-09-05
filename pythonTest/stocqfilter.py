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
import locale
from locale import atof
import os
from argparse import ArgumentParser

MODE = "mon"
TW_STOCK_SERVER = "https://mops.twse.com.tw"
REFETCH = 1

# TODO: 找出今年配息, 殖利率等相關資訊
def get_html_dfs(stryear, strmonth, action):
    year = int(stryear)
    month = int(strmonth)
    monthly_file = "./mon_" + stryear + "_" + strmonth + ".html"
    if (action == 'refresh'):
        print("Refetch html..")
        open(monthly_file, 'a').close()
        os.remove(monthly_file)
    try:
        with open (monthly_file, 'r') as mf:
            dfs = pd.read_html(monthly_file, encoding='utf-8')
            print ("read html file successfully")
            return dfs
    except Exception as e:
        print(e)
        if year > 1990:
    	    year -= 1911
    
        url = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'_0.html'
        if year <= 98:
        	url = 'http://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'.html'
    
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    
        r = requests.get(url, headers=headers)
        r.encoding = 'big5'
        print ("fetch html file successfully")
        #print(url)
        #print(r.text)
    
        with codecs.open( monthly_file, mode='wb') as writefile:
            writefile.write(r.text.encode('utf8'))
        dfs = pd.read_html(StringIO(r.text), encoding='big-5')
        return dfs

def monthly_report(year, month, action='None'):
    dfs = get_html_dfs(year, month, action)
    #print dfs[1].describe

    df = pd.concat([df for df in dfs if df.shape[1] <= 11 and df.shape[1] > 5])
    print(df.columns.tolist())
    
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
    wlist = ['5283', '2610', '1229', '1722', '2330', '2103', '8926', '2535', '3705', '2439', '2634', '6201', '2375', '9946', '1730', '6214', '2105']
    #Directors and Supervisors 董監持股% 排行
    top_dshold_list = ['2227', '2630', '8455', '1525', '6236', '6505', '5450', '3532', '8908', '2007', '8931', '3093', '5344', '2748', '4545', '6023', '1535', '9930', '6581', '1232', '3489', '2468', '8046', '6577', '3016', '8454', '2029', '5468', '8473', '8420', '1735', '4989', '8480', '1789', '5902', '3564', '8426', '3709', '2433', '8032', '1736', '8077', '3628', '1795', '6613', '2724', '6103', '3226', '2633', '6523', '6499', '4919', '1259', '9928', '6451', '6579', '6227', '6514', '6441', '5820', '4763', '6291', '3652', '6640', '6803', '8291', '1530', '2397', '5288', '5264', '6616', '4192', '2923', '6654', '1256', '8923', '6561', '1905', '2221', '8432', '6548', '6024', '4506', '8182', '3073', '3675', '2851', '2722', '2528', '3691', '6114', '6552', '3067', '6482', '6196', '6230', '6021', '6594', '2429', '3623', '8099', '2427', '1439', '5903', '8418', '1617', '3083', '2373', '3144', '2926', '2836', '2719', '8424', '2204', '3454', '3265', '3054', '6144', '2712', '8913', '2642', '8404', '6525', '4180', '1592', '2596', '6488', '6582', '4755', '5465', '6569', '3631', '5907', '5209', '3685', '4933', '9906', '1773', '4188', '2939', '1583', '2543', '6412', '8406', '5340', '8499', '4807', '6241', '6183', '4432', '6221', '6674', '2607', '2901', '1418', '8104', '6486', '6435', '6248', '9907', '8444', '3624', '4552', '4173', '3666', '3188', '3031', '3515', '8131', '8279', '8934', '6669', '3004', '3512', '4528', '8463', '6134', '2609', '4563', '2540', '2729', '4148', '5223', '2438', '3416', '1309', '2912', '8067', '9941', '2723', '3663', '8101', '6171', '8466', '8427', '6609', '4706', '2035', '3276', '1235', '5347', '4566', '2916', '6574', '1724', '5102', '6173', '4930', '3171', '6461', '3162', '4131', '8367', '2610', '2441', '5234', '6666', '3294', '1726', '4116', '6541', '5317', '4944', '1802', '2009', '4433', '1258', '4438', '4523', '8415', '2013', '4538', '8921', '2643', '8440', '5210', '3465', '6516', '4702', '2904', '4554', '4420', '6222', '5212', '9950', '3570', '6284', '5011', '3504', '6431', '4535', '2440', '8446', '1109', '1702', '2867', '2606', '5276', '4419', '4737', '4560', '9918', '2739', '4912', '5508', '3374', '6191', '3287', '8201', '6130', '1737', '3310', '8110', '5269', '8215', '2014', '3046', '6228', '3492', '1339', '3558', '2450', '4725', '2390', '6140', '1308', '3557', '2462', '3380', '4958', '3611', '5703', '3332', '8072', '2239', '4175', '4157', '6590', '4154', '8341']

    tdsh_df = wdf = df[df['ID'].isin(top_dshold_list) == True]
    print ("Top Directors & Supervisor Holding % List_________\n")
    print (wdf.iloc[0:25, [0,2,3,4,5,6,7,8,9,1,10]])
    print ("\n")

    wdf = df[df['ID'].isin(wlist) == True]
    print ("White List_________\n")
    print (wdf.iloc[0:25, [0,2,3,4,5,6,7,8,9,1,10]])
    print ("\n")

    df = df[df['MOM%'] > 3]
    df = df[df['YOY%'] > 3]
    df = df[df['%AccYoY'] > 3.0]
    df = df[df['ID'].isin(blacklist) == False]
    df = df.sort_values(['%AccYoY'])
    #print ("df.columns")
    #print (df.columns)
    row_cnt, col_cnt = df.shape
    idx = 0
    while idx < row_cnt:
        print (str(year) + " " + str(month) + "th " + "monthly Good")
        print (df.iloc[idx : idx+10, [0,2,3,4,5,6,7,8,9,1,10]])
        idx = idx + 10
    return df

def get_html_dfs_fin_stat(year, season, type):
    fin_stat_file = "./fin" + str(year) + "_" + str(season) + ".html"
    print ("Handle fin stat: " + fin_stat_file)
    if (0 != REFETCH):
        open(fin_stat_file, 'a').close()
        os.remove(fin_stat_file)
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
            url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb04'
        elif type == '資產負債彙總表':
            url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb05'
        elif type == '營益分析彙總表':
            url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb06'
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
        print(r.text)
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
    majordf = majordf.iloc[:, [0,    2,        3,       5,          10,     12,      13,            19,        20,    22,   29,    1     ] ]
    majordf.columns =         ["ID", "income", "Costs", "NetGross", "fees", "OpPft", "NonOpIn", "NetProf", "OCI", "CI", "EPS", "name"]


    # Gross Profit Margin rate
    di = {"--" : 0}
    majordf.income = majordf.income.map(di).fillna(majordf.income).astype(float)
    majordf.Costs = majordf.Costs.map(di).fillna(majordf.Costs).astype(float)
    majordf['gpm'] = (majordf.income.astype(float) - majordf.Costs.astype(float))/majordf.income.astype(float) * 100.0
    cols = majordf.columns.tolist()
    cols = cols[0:3] + cols[-1:] + cols[3:-1]
    #print(cols)
    majordf = majordf[cols]

    # Net Profit Margin rate
    di = {"--" : 0}
    majordf.NetProf = majordf.NetProf.map(di).fillna(majordf.NetProf).astype(float)
    majordf['npm'] = majordf.NetProf.astype(float) / majordf.income.astype(float) * 100.0
    cols = majordf.columns.tolist()
    cols = cols[0:9] + cols[-1:] + cols[9:-1]
    #print(cols)
    majordf = majordf[cols]

    majordf = majordf[majordf['EPS'] > 0.0]
    majordf = majordf[majordf['gpm'] > 5.0]
    majordf = majordf[majordf['npm'] > 5.0]
    white_list = monthly_report("108", "4")
    majordf = majordf.loc[majordf['ID'].isin(white_list['ID'])]

    # digit print format: 1,234,567
    for col in ['income', 'Costs','OpPft', 'NetProf', 'CI', 'NonOpIn']:
        majordf[col] = majordf.apply(lambda x: "{:,}".format(x[col]), axis=1)

    majordf = majordf.sort_values(['npm'])
    idx = 0
    row_cnt, col_cnt = majordf.shape
    while idx < row_cnt: 
        print ("\n" + str(year) + " season" + str(season) + "__" + str(idx) + " to " + str(idx+10))
        print(majordf[idx : idx+10])
        idx = idx + 10
    return True

#FIXME:
def get_daily_html(datestr):
    filename = datestr + ".txt"
    try:
        dfs = pd.read_html(filename, encoding='utf-8')
        print ("read html file successfully")
        return dfs
    except Exception as e:
        r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')
        with codecs.open( datestr + ".txt", mode='wb') as writefile:
            writefile.write(r.text.encode('utf8'))
        df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
                                     for i in r.text.split('\n') 
                                     if len(i.split('",')) == 17 and i[0] != '='])), header=0, thousands=',')
        return df


def daily_report(datestr):
    r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')
    with codecs.open( datestr + ".txt", mode='wb') as writefile:
        writefile.write(r.text.encode('utf8'))

    print("Date: " + datestr)
    df = pd.read_csv(StringIO("\n".join([line.translate({ord(c): None for c in ' '}) 
                                     for line in r.text.split('\n') 
                                     if len(line.split('",')) == 17 and line[0] != '='])), header=0, thousands=',')
    #print(df.columns.tolist())

    df = df.iloc[:, [0,    1,      2,            3,         4,       5,      6,      7,        8,       9,       10,     11,        12,      13,        14,      15  ] ]
    df.columns =    ["ID", "name", "DealShares", "DealCnt", "Deal$", "Open", "Peek", "Low", "Final", "Diff%", "Diff", "LBPrice", "LBAmt", "LSPrice", "LSAmt", "PERatio"]
    cols = df.columns.tolist()
    cols = cols[0:1] + cols[2:11] + cols[15:16] + cols[1:2]
    df = df[cols]

    '''
    # Translate non float strings
    #FIXME
    di = {"--" : 0, "4,455.00" : 4455.00, "4,365.00": 4365.00, "4,510.00":4510.00, "4,725.00":4725.00, "1,740.00":1740.00, "4,410.00":4410.00, "1,730.00":1730.00, "4,400.00": 4400.00}
    df.Peek=df.Peek.map(di).fillna(df.Peek).astype(float)
    df.Final=df.Final.map(di).fillna(df.Final).astype(float)
    df.Low=df.Low.map(di).fillna(df.Low).astype(float)

    #locale.setlocale(locale.LC_NUMERIC, '')
    #df.iloc[:,6:9].applymap(atof)

    # Find the strong ones
    strongIndex = (df['Final'] - df['Low']) / (df['Peek'] - df['Low'])
    print(strongIndex[(strongIndex > 0.8) & ((df['Peek'] / df['Low'] > 1.02))].sort_values(ascending=False))
    return
    '''

    gt3 = df[pd.to_numeric(df['PERatio'], errors='coerce') > 3]
    gt3lt10 = gt3[pd.to_numeric(df['PERatio'], errors='coerce') < 10]
    print(df.columns.tolist())
    print (strongIndex[:10])
    return df

def parse_commands():
    parser = ArgumentParser()
    subcmd = parser.add_subparsers()
    subcmd.required = True

    grp_twss = subcmd.add_parser('twss', help='TW stock server')
    grp_twss.add_argument("--mode", type=str, help="mon, fin, today, yesterday")
    # Server
    help_str = "TW stock server address, default = " + str(TW_STOCK_SERVER)
    grp_twss.add_argument("--twss_addr", type=str, help=help_str)
    grp_twss.add_argument("--refetch",   type=int, help="refetch the file")

    return parser.parse_args()

if __name__ == '__main__':
    # Handle Arguments
    args = parse_commands()
    print(args)

    if args.mode is not None:
        MODE = args.mode
    if args.twss_addr is not None:
        TW_STOCK_SERVER = str(args.twss_addr)
    if args.refetch is not None:
        REFETCH = args.refetch

    now = datetime.datetime.now()
    print("today:" + str(now.year) + " " + str(now.month) + " " + str(now.day))


    if ("today" == MODE):
        datestr = str(now.year) + str(now.month).zfill(2) + str(now.day-1).zfill(2)
        daily_report(datestr)
    elif ("yesterday" == MODE):
        datestr = str(now.year) + str(now.month).zfill(2) + str(now.day-2).zfill(2)
        daily_report(datestr)
    elif ("mon" == MODE):
        monthly_report("108", "8", REFETCH)
    elif ("fin" == MODE):
        try:
            financial_statement(108, 2)
            #if (True != financial_statement(108, 2)):
            #    financial_statement(108, 1)
        except Exception as e:
            print(e)

