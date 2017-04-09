import tushare as ts
import datetime
import pandas as pd
import sqlite3API

#取得上市天数
#df = (ts.get_stock_basics())
#df.to_excel('stock_list.xlsx')

#取得流通市值
#df_liutong = ts.get_today_all()
#df_liutong.to_excel('stock_liutong.xlsx')

#df_tick_data = ts.get_tick_data('603701',date='2017-03-08')
#df_tick_data.to_excel('tick_data.xlsx')

#df_new = df[df['timeToMarket']>'20150101']

#print(df_new.ix[])

def test_df():
    aa={'one':[1,2,3],'two':[2,3,4],'three':[3,4,5]}
    bb=pd.DataFrame(aa,index=['first','second','third'])

    print(bb)
    print(bb.ix['second']['one'])

    d1 = datetime.datetime.strptime('20150216', '%Y%m%d')

    #d1 = datetime.datetime(20150216)
    d2 = datetime.datetime.now()
    print((d2-d1).days)

def test_sqlite():

    stock_list=['002858','603041','002857','603388','603178','002816','603031','603701','603991','002806','603319','002796','603090','603038','603990','603029','002800','603908','002810','002837','002835','603738','002805','603960','603266','603037','603819','603633','603887','002856','603033','603663','002830','603637','603089','603032','002808']
    conn = sqlite3API.get_conn('stock.db')
    sql_tid ="select code,timeToMarket from stock_info where code in ('" + "','".join(stock_list) + "')"
    info_tid=sqlite3API.fetchmany(conn,sql_tid)
    dic = dict()
    for info_temp in info_tid:
        dic[info_temp[0]] = info_temp[1]
    print(dic)

if __name__ == '__main__':
    test_sqlite()