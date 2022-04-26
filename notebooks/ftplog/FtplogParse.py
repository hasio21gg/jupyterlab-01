#!/usr/bin/env python
# coding: utf-8

# #### FTP(IIS)のログを解析する
# ##### IN : IIS(FTP)のログ置き場にSMBで取得、必要情報
# ##### OUT:
# 
# https://sinhrks.hatenablog.com/entry/2014/11/21/231534

# ###### 必要ライブラリ

# In[ ]:


#get_ipython().system('pip install pysmb')


# In[1]:


from smb.SMBConnection import SMBConnection
import platform
import pandas as pd
import re
import io
import datetime as dt
from pathlib import Path
#from tqdm import tqdm
from tqdm.auto import tqdm
import typer
#import os
import gc

#import json
import pickle


# In[2]:


global order
global logs_head
order = [
        "date","time","c-ip","cs-username","s-ip",
        "s-port","cs-method","cs-uri-stem","sc-status","sc-win32-status",
        "sc-substatus","time-taken","x-session","x-fullpath"]
logs_head = [
    'c-ip','cs-username','s-ip','s-port',
    'cs-method','cs-uri-stem','sc-status','sc-win32-status',
    'sc-substatus','time-taken','x-session','x-fullpath','timestamp']


global FILE_NUMBER
FILE_NUMBER = 0


# In[3]:


def envset(argLOG_YMD, argYMD):
    global ENV
    global ip_address
    global user
    global password
    global remote_hostname 
    global LOG_YMD
    global SHARE_NAME
    global FILE_TO_PATH
    global HOME_PATH
    global OUT_PATH
    global LOG_PATH
    global YMD
    global OUT_FILE
    global picklepath
    global OUT_SUM_FILE
    
    LOG_YMD = argLOG_YMD
    ENV = 'HONBAN'    
    #ENV = 'TEST'
    if(ENV == 'TEST'):
        ip_address = '172.30.9.85'
        user = 'Administrator'
        password = 'panic'
        remote_hostname = 'RGSV920'
    else:
        ip_address = '172.30.4.193'
        user = 'Administrator'
        password = 'panic'
        remote_hostname = 'SESV400'

    SHARE_NAME = 'd$'
    FILE_TO_PATH = 'Ftp/Logs/2021/'
    FILE_TO_PATH = 'Ftp/Logs/2022/'
    HOME_PATH = '/home/jovyan/'
    OUT_PATH = HOME_PATH + 'datasets/Ftplogs/Output/'
    LOG_PATH = f'{HOME_PATH}datasets/Ftplogs/{remote_hostname}/'
    #YMD = f'%s' % dt.datetime.now().strftime('%Y%m%d')
    YMD = argYMD
    #
    #OUT_FILE = f'{OUT_PATH}Log/{YMD}_{remote_hostname}_{LOG_YMD}_{FILE_NUMBER}_FtpLogs.csv'
    #picklepath = f'{OUT_PATH}Pickle/{YMD}_{remote_hostname}_{LOG_YMD}_{FILE_NUMBER}_FtpLogs.csv.pickle'
    #OUT_SUM_FILE = f'{OUT_PATH}Sumary/{YMD}_{remote_hostname}_{LOG_YMD}_{FILE_NUMBER}_FtpLogsSumary.csv'
    
    print(f'%-20s:{ENV:<15s}' % ("ENV"))
    print(f'%-20s:{ip_address:<15s}' % ("ip_address"))
    print(f'%-20s:{user:<15s}' % ("user"))
    print(f'%-20s:{password:<15s}' % ("password"))
    print(f'%-20s:{remote_hostname:<15s}' % ("remote_hostname"))
    print(f'%-20s:{SHARE_NAME:<15s}' % ("SHARE_NAME"))
    print(f'%-20s:{OUT_PATH:<15s}' % ("OUT_PATH"))
    print(f'%-20s:{LOG_PATH:<15s}' % ("LOG_PATH"))
    print(f'%-20s:{YMD:<15s}' % ("YMD"))
    print(f'%-20s:{LOG_YMD:<15s}' % ("LOG_YMD"))
    
   


# In[4]:


def filenames(argFILE_NUMBER):
    
    global OUT_FILE
    global picklepath
    global OUT_SUM_FILE
    
    OUT_FILE = f'{OUT_PATH}Log/{YMD}_{remote_hostname}_{LOG_YMD}_{argFILE_NUMBER:02}_FtpLogs.csv'
    picklepath = f'{OUT_PATH}Pickle/{YMD}_{remote_hostname}_{LOG_YMD}_{argFILE_NUMBER:02}_FtpLogs.csv.pickle'
    OUT_SUM_FILE = f'{OUT_PATH}Sumary/{YMD}_{remote_hostname}_{LOG_YMD}_FtpLogsSumary.csv'
    
    print(f'%-20s:{OUT_FILE:<15s}' % ("OUT_FILE"))
    print(f'%-20s:{picklepath:<15s}' % ("picklepath"))
    print(f'%-20s:{OUT_SUM_FILE:<15s}' % ("OUT_SUM_FILE"))
 


# In[5]:


#
def SMBFileList():
    print("==================================================")
    result = False
    conn = SMBConnection(
        user,
        password,
        platform.uname().node,
        remote_hostname,
        domain='WORKGROUP',
        use_ntlm_v2=True)
    result = conn.connect(ip_address, 139)
    print(result)
    return result, conn


# In[6]:


def LogRead(filename, arg1):
    #df =pd.DataFrame(columns = order)
    def proc1(lines):
        cnt = 0
        all = len(lines)
        bar_template = ""
        for buf in lines:
            cnt+=1
            print(f'\r{filename:_<10}:{cnt:07}/{all:07} [{cnt/all:.2%}]', end="")
            _line = buf.decode() if arg1 == 1 else buf
            if not re.search('^#', _line):
                (
                    date,time,cip,csusername,sip,
                    sport,csmethod,csuristem,scstatus,scwin32status,
                    scsubstatus,timetaken,xsession,xfullpath
                ) = _line.split(' ')
                df.loc[len(df)] = [
                    date,time,cip,csusername,sip,
                    sport,csmethod,csuristem,scstatus,scwin32status,
                    scsubstatus,timetaken,xsession,xfullpath
                ]
    def proc2(filepath):
        txt = Path(filepath).resolve()
        length = sum(1 for row in open(txt, 'r'))
        chunksize = 5000
        df_t = pd.DataFrame()
        typer.secho(f"Reading file: {txt}", fg="red", bold=True)
        #typer.secho(f"total rows: {length}", fg="green", bold=True)
        with tqdm(total=length, desc="chunks read: ") as bar:
            dsz = length
            for i, chunk in enumerate(pd.read_csv(txt, 
                                                  chunksize=chunksize, 
                                                  low_memory=False, 
                                                  header = None, 
                                                  #skiprows=4, 
                                                  comment='#',
                                                  sep=' ', 
                                                  names=order,
                                                  parse_dates={'timestamp':['date', 'time']}
                                                  )):
                df_t = pd.concat([df_t,chunk])
                bar.update(min(dsz, chunksize))
                dsz -= chunksize
        #typer.secho("end of reading chunks...", fg=typer.colors.BRIGHT_RED, end="")
        #typer.secho(f"Dataframe length:{len(df_t)}", fg="green", bold=True)
        return df_t
    if(arg1 == 1):
        # 遅いので使わない
        with io.BytesIO() as file:
            conn.retrieveFile(SHARE_NAME, FILE_TO_PATH + filename, file)
            file.seek(0)
            proc1(file.read().splitlines())
        file.close()
    elif(arg1 == 2):
        # 遅いので使わない
        with open(LOG_PATH + filename) as file:
            proc1(file.read().splitlines())
        file.close()
    elif(arg1 == 3):
        df = proc2(LOG_PATH + filename)
        #df = pd.read_csv(LOG_PATH + filename, header = None, skiprows=4, sep=' ', names=order)
        #return df
        #df_res = pd.concat([df_res, df])
        #print("--------------------------- concat ")
        #print(df_res.dtypes)
    else:
        print(2)        
    return df


# In[7]:


def LogWrite(filename, conn):
    with open(LOG_PATH + filename, 'wb') as file:
        conn.retrieveFile(SHARE_NAME, FILE_TO_PATH + filename, file)
    return 1


# In[8]:


def main(argLOG_YMD, argYMD = f'%s' % dt.datetime.now().strftime('%Y%m%d')):
    #print("[main]")
    #LOG_YMD = argLOG_YMD
    envset(argLOG_YMD, argYMD)

    #SMBコネクション生成
    #ret, conn = SMBFileList()
    ret ,conn = SMBFileList()
    assert ret == True

    #SMBファイル一覧
    #items = []
    items = conn.listPath(
        SHARE_NAME,
        FILE_TO_PATH
    )
    assert len(items) > 0
            
    #FTPログヘッダー
    #order = [
    #    "date","time","c-ip","cs-username","s-ip",
    #    "s-port","cs-method","cs-uri-stem","sc-status","sc-win32-status",
    #    "sc-substatus","time-taken","x-session","x-fullpath"
    #]
    #FTPログDataFrame
    df_res = pd.DataFrame(columns = order)
    df_concat = pd.DataFrame(columns = logs_head)
    #print('<==========>')
    def proc1(argfilename, df_concat, df_res, OUT_FILE):
        df_concat = pd.concat([df_concat, df_res])
        df_concat = df_concat.drop(['date','time'], axis=1) 
        #print(OUT_FILE)
        df_concat.index = pd.DatetimeIndex(df_concat.timestamp, name='timestamp')
        df_concat.index = df_concat.index.tz_localize('UTC')
        df_concat.index = df_concat.index.tz_convert('Asia/Tokyo')
        df_concat.timestamp = df_concat.index
        df_concat = df_concat.reset_index(drop=True)
        df_concat.to_csv(OUT_FILE)
        #print(df_concat.info())
        df_concat.to_pickle(picklepath)
    
    #print('<==========>')
    FILE_NUMBER = 0
    FILE_SIZE = 300000000
    FILE_SIZE_CUR = 0
    filenames(FILE_NUMBER)
    
    for item in items:
        #print(f'%s %d bytes' % (item.filename, item.alloc_size)) 
        if(not item.isDirectory and 
            re.search(LOG_YMD, item.filename)):
            print(f'%s %d bytes' % (item.filename, item.alloc_size)) 
            FILE_SIZE_CUR += item.alloc_size
            if(int(FILE_SIZE_CUR/FILE_SIZE) > 0):
                FILE_NUMBER += 1
                FILE_SIZE_CUR = item.alloc_size
                proc1(item.filename, df_concat,df_res, OUT_FILE)
                df_res = df_res[:0]
                df_concat = df_concat[:0]
                gc.collect()                
                
            filenames(FILE_NUMBER)
            LogWrite(item.filename, conn)
            df_res = pd.concat([df_res, LogRead(item.filename, 3)])
            
    conn.close()
    
    proc1(item.filename, df_concat,df_res, OUT_FILE)
    df_res = df_res[:0]
    df_concat = df_concat[:0]
    gc.collect()                
    return FILE_NUMBER
    #assert 0 > 1


# In[9]:


def recov(FILE_NUMBER, argLOG_YMD, argYMD = f'%s' % dt.datetime.now().strftime('%Y%m%d')):
    envset(argLOG_YMD, argYMD)
    filenames(FILE_NUMBER)
    #picklepath = f'{OUT_PATH}{YMD}_{remote_hostname}_{argLOG_YMD}_FtpLogs.csv.pickle'
    with open(picklepath, mode='rb') as fp:
        df_concat = pickle.load(fp)
    
    df_concat['index'] = df_concat.reset_index().index
    print(len(df_concat['x-session'].unique()))
    df_min = df_concat.groupby('x-session', as_index=False)[['index','timestamp']].min()
    df_max = df_concat.groupby('x-session', as_index=False)[['index','timestamp']].max()
    df_min = df_min.rename(columns={'index':'index_min', 'timestamp':'timestamp_min'})
    df_max = df_max.rename(columns={'index':'index_max', 'timestamp':'timestamp_max'})
    df2 = pd.merge(df_min,df_max, on='x-session')
    
    df_group = df_concat.groupby(['x-session','c-ip','s-ip'], as_index=False)[['index']].min()
    #print(df_group.info())
    
    df3 = pd.merge(df2,df_group, on='x-session')

    df3['timestamp_diff'] = df3['timestamp_max'] - df3['timestamp_min']
    #df3['timestamp_ts'] = df3['timestamp_diff'].map(lambda x: x.total_seconds())
    df3['timestamp_ts'] = df3['timestamp_diff'].dt.total_seconds() + 1
    #display(df3)
    df3 = df3.drop(['index','timestamp_diff'], axis=1) 
    df3['timestamp'] = df3['timestamp_min'].dt.strftime('%Y/%m/%d %H:%M:%S')
    df3['count'] = 1
    #
    print(df3.info())
    ##df3.to_csv(OUT_SUM_FILE)
    return df3


# In[10]:


def graph(df3):
    import matplotlib.pyplot as plt
    import collections
    import itertools
    import warnings
    warnings.filterwarnings('ignore')
    # matplotlib日本語化対応
    import japanize_matplotlib

    all_from_list = df3['c-ip'].tolist()
    c = collections.Counter(df3['c-ip'].tolist())

    tags = pd.Series(c)
    #print(tags)
    df4 = df3.copy()
    df4.set_index('timestamp_min', inplace=True)

    df_tag_list = []
    # 先頭10
    top_tag_list = tags.sort_values(ascending=False).index.tolist()

    for t in top_tag_list:
        print(t)
        df_tag = df3[df3['c-ip'].apply(lambda x: t in x)]
        df_tag_list.append(df4[['timestamp_ts']].resample('H').sum())

    df_tags = pd.concat(df_tag_list, axis=1)
    df_tags.columns = top_tag_list

    df_tags[:-1].plot(stacked=True,figsize=(10, 4), title='上位10接続推移')
    plt.legend(title="接続先", bbox_to_anchor=(1.05, 1)) # <-- ココ
    plt.show()

    df_tags[:-1].plot.bar(stacked=True, figsize=(10, 4), title='上位10接続推移積み上げ')
    plt.legend(title="接続先", bbox_to_anchor=(1.05, 1)) # <-- ココ
    plt.show()


# In[11]:


#lp = ['21010','21011','21012'] #20220323
#lp = ['21013','21022','21022'] #20220325
#lp = ['21030','21031','21032','21033']  #20220325
#lp = ['21040','21041','21042','21043']  #20220325
#lp = ['21050','21051','21052','21053']  #20220325
#lp = ['21060','21061','21062','21063']  #20220325
#lp = ['21070','21071','21072','21073']  #20220325
#lp = ['21080','21081','21082','21083']  #20220328
#lp = ['21090','21091','21092','21093']  #20220328
# #lp = ['21100','21101','21102','21103']  #20220328
# #lp = ['21102']  #20220328-1 ['211020','211021','211022','211023','211024','211025']
# #lp = ['21102']  #20220328-1 ['211026','211027','211028','211029']
# #lp = ['21103']  #20220328
#lp = ['2110']  #20220329
#lp = ['2111']  #20220329
#lp = ['2112']  #20220329
#lp = ['2201']  #20220329
lp = ['2202']  #20220329
df = pd.DataFrame()
for l in lp:
    print(f'[IN] YMD: {l}')
    n = main(l)
    for i in range(n):
        df = pd.concat([df, recov(i, l)])
        
    df.to_csv(OUT_SUM_FILE)
    #graph(recov(l, n))


# In[ ]:




