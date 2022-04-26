#!/usr/bin/env python
# coding: utf-8

# In[1]:



import datetime as dt
import pandas as pd


# In[2]:


def envset(
    argLOG_YMD = f'%s' % dt.datetime.now().strftime('%Y%m%d'),
    argYMD     = f'%s' % dt.datetime.now().strftime('%Y%m%d')
    ):
    global HOME_PATH    
    LOG_YMD = argLOG_YMD
    HOME_PATH = '/home/jovyan/'
    print(f'%-20s:{LOG_YMD:<15s}' % ("LOG_YMD"))
    print(f'%-20s:{HOME_PATH:<15s}' % ("HOME_PATH"))


# In[3]:


def a(csv_file):
    df = pd.read_csv(csv_file, index_col='timestamp',parse_dates=['timestamp'])
    return df

envset()

files = [
    '20220323_SESV400_21010_FtpLogsSumary.csv',
    '20220323_SESV400_21011_FtpLogsSumary.csv',
    '20220323_SESV400_21012_FtpLogsSumary.csv',
    '20220325_SESV400_21013_FtpLogsSumary.csv',
    '20220325_SESV400_21020_FtpLogsSumary.csv',
    '20220325_SESV400_21022_FtpLogsSumary.csv',
    '20220325_SESV400_21030_FtpLogsSumary.csv',
    '20220325_SESV400_21031_FtpLogsSumary.csv',
    '20220325_SESV400_21032_FtpLogsSumary.csv',
    '20220325_SESV400_21033_FtpLogsSumary.csv',
    '20220325_SESV400_21040_FtpLogsSumary.csv',
    '20220325_SESV400_21041_FtpLogsSumary.csv',
    '20220325_SESV400_21042_FtpLogsSumary.csv',
    '20220325_SESV400_21043_FtpLogsSumary.csv',
    '20220325_SESV400_21050_FtpLogsSumary.csv',
    '20220325_SESV400_21051_FtpLogsSumary.csv',
    '20220325_SESV400_21052_FtpLogsSumary.csv',
    '20220325_SESV400_21053_FtpLogsSumary.csv',
    '20220325_SESV400_21060_FtpLogsSumary.csv',
    '20220325_SESV400_21061_FtpLogsSumary.csv',
    '20220325_SESV400_21062_FtpLogsSumary.csv',
    '20220325_SESV400_21063_FtpLogsSumary.csv',
    '20220325_SESV400_21070_FtpLogsSumary.csv',
    '20220325_SESV400_21071_FtpLogsSumary.csv',
    '20220325_SESV400_21072_FtpLogsSumary.csv',
    '20220325_SESV400_21073_FtpLogsSumary.csv',
]
files = [
#    '20220328_SESV400_21080_FtpLogsSumary.csv',
 #   '20220328_SESV400_21081_FtpLogsSumary.csv',
  #  '20220328_SESV400_21082_FtpLogsSumary.csv',
   # '20220328_SESV400_21083_FtpLogsSumary.csv',
    #'20220328_SESV400_21090_FtpLogsSumary.csv',
    #'20220328_SESV400_21091_FtpLogsSumary.csv',
    #'20220328_SESV400_21092_FtpLogsSumary.csv',
    #'20220328_SESV400_21093_FtpLogsSumary.csv',
    #'20220329_SESV400_2110_FtpLogsSumary.csv',
    #'20220329_SESV400_2111_FtpLogsSumary.csv',
    #'20220329_SESV400_2112_FtpLogsSumary.csv',
    '20220329_SESV400_2201_FtpLogsSumary.csv',
]

df_month = pd.DataFrame()
print(len(files))
for f in files:
    print(f)
    df_month = pd.concat([df_month, a(f'{HOME_PATH}datasets/Ftplogs/Output/Sumary/{f}')])
    
df_month_aft = df_month.set_index([df_month.index.weekday,df_month.index])
df_month_aft.index.names = ["weekday","timestamp",]
df_month_aft.sort_index()
#print(df_month_aft.sum(level='weekday'))
#display(df_month)
#df_month.index.names = ["timestamp", "weekday_name"]
#print(df_month_aft.info())


# In[ ]:


#print(df_month_aft.groupby([pd.Grouper(key='weekday'),'c-ip']).sum()[['count','timestamp_ts']])


# In[ ]:


#df_month.groupby([pd.Grouper(key='weekday'),'c-ip']).sum()[['count','timestamp_ts']]


# In[ ]:


#(df_month.groupby([pd.Grouper(freq='D'),'c-ip']).sum()[['count','timestamp_ts']]).to_csv('2022-2Q.csv')


# In[ ]:


#print((df_month.groupby([pd.Grouper(freq='weekday'),'c-ip']).sum()[['count','timestamp_ts']]).info())


# In[ ]:


#df_month.groupby([pd.Grouper(freq='D'),pd.Grouper(freq='W'),'c-ip']).sum()[['count','timestamp_ts']]


# In[11]:


df_g = (df_month_aft.groupby(['weekday','c-ip']).sum()[['count']])

print(df_g.head(10))

# In[12]:


#df_g.plot()


# In[ ]:




