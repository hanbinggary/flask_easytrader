import tushare as ts
import datetime
import pandas as pd
import sqlite3API
import json
import sqlite3 as lite
import easyquotation
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
    print(type(info_tid))
    print(info_tid)
    dic = dict()
    for info_temp in info_tid:
        dic[info_temp[0]] = info_temp[1]
    print(dic)

#tushare 取上市日期
def getIpoInfo():
    
    try:
        #上市日期取得
        df = (ts.get_stock_basics())
        if len(df)>3000:
            cnx = lite.connect('stock.db')
            df.to_sql('stock_info',con=cnx,flavor='sqlite', if_exists='replace')
            print( 'get ipo OK')
        else:
            print('get_stock_basics error.')
    except:
        print( 'get ipo error')
        
#tushare 取流通市值
def getLiutong():
    
    try:
        #取得流通市值
        df = ts.get_today_all()
        cnx = lite.connect('stock.db')
        if len(df) > 3000:
            df.to_sql('liutong_info',con=cnx,flavor='sqlite', if_exists='replace')
            print( 'get liutong OK')
        else:
            print('get_today_all error')
    except:
        print( 'get liutong error')

def tq_test():
    
    q = easyquotation.use('qq')

    #取上市300天内的最小流通市值 top 40
    dic,stock_list = gettimeToMarket()

    #stock_list=['002858','603041','002857','603388','603178','002816','603031','603991','002806','603319','603090','603038','603990','603908','002810','002837','002835','603738','002805','603960','603266','603037','603819','603633','603887','002856','603033','603663','002830','603637','603089','603032','002808']
    stockinfo,stockinfo_zhangting = q.stocks(stock_list)

    temp = sorted(stockinfo.items(), key=lambda d:d[1]['流通市值'])

    #最小流通市值取得
    min_liutong = min(stockinfo.items(), key=lambda d:d[1]['流通市值'])[1]
    #计算流通市值差
    
    for key,value in stockinfo.items():
        try:
            #市值差 （流通市值/最小流通市值）-1
            stockinfo[key]['cha'] = str(round((float(stockinfo[key]['流通市值'])/float(min_liutong['流通市值']) - 1)*100,2)) + '%'
            #去损耗市值差  （流通市值*现价/买1价）/（最小流通市值*现价/卖1价）-1
            liutong_sunhao = stockinfo[key]['流通市值']*stockinfo[key]['bid1']/stockinfo[key]['now']
            min_liutong_sunhao = min_liutong['流通市值']*min_liutong['ask1']/min_liutong['now']
            stockinfo[key]['cha_sunhao'] = str(round((liutong_sunhao/min_liutong_sunhao - 1)*100,2)) + '%'
            #上市天数计算
            d1 = datetime.datetime.strptime(dic[key], '%Y%m%d')
#            print(d1)
            ipo_date_num = (datetime.datetime.now()-d1).days
            stockinfo[key]['ipo_date_num'] = ipo_date_num if ipo_date_num > 50 else str(ipo_date_num) + ' 天'
            stockinfo[key]['ipo_date_num_css'] = 'font-red-bold' if ipo_date_num <= 50 else ''
        except Exception as e:
            print(e)

    for key,value in stockinfo_zhangting.items():
        try:
            #上市天数计算
            d1 = datetime.datetime.strptime(dic[key], '%Y%m%d')
            ipo_date_num = (datetime.datetime.now()-d1).days
            stockinfo_zhangting[key]['ipo_date_num'] = ipo_date_num if ipo_date_num > 50 else str(ipo_date_num) + '天'
        except:
            pass

#    return render_template('post_test.html', stockinfo_zhangting=stockinfo_zhangting,stockinfo_sort=temp)

#从本地sqlite取得上市日期
def gettimeToMarket():

    conn = sqlite3API.get_conn('stock.db')
    #sql_tid ="select code,timeToMarket from stock_info where code in ('" + "','".join(stock_list) + "')"
    sql_tid='''
        select stock_info.code,stock_info.timeToMarket from liutong_info 
        inner join stock_info on
        liutong_info.code = stock_info.code
        where liutong_info.nmc<120000 and substr(liutong_info.code,1,1) != '3' 
        and substr(stock_info.timeToMarket,1,4) || '-' || substr(stock_info.timeToMarket,5,2) || '-' || substr(stock_info.timeToMarket,7,2) > date('now','-300 days')
        order by liutong_info.nmc 
        limit 40;
        '''
    info_tid=sqlite3API.fetchmany(conn,sql_tid)
    dic = dict()
    stock_list=[]
    for info_temp in info_tid:
        dic[info_temp[0]] = str(info_temp[1])
        stock_list.append(info_temp[0])
    
    return dic,stock_list     

def getCixinCode():
    conn = sqlite3API.get_conn('stock.db')

    sql_tid='''
        select code from stock_info 
        where substr(stock_info.timeToMarket,1,4) || '-' || substr(stock_info.timeToMarket,5,2) || '-' || substr(stock_info.timeToMarket,7,2) > date('now','-300 days') 
        and substr(code,1,1) != '3' ;
        '''
    info_tid=sqlite3API.fetchmany(conn,sql_tid)
    stock_list=[]
    for info_temp in info_tid:
        stock_list.append(info_temp[0])
    
    return stock_list     

def getLiutong_from_qq():
    q = easyquotation.use('qq')

    #取上市300天内的股票
    stock_list = getCixinCode()
    stockinfo,stockinfo_zhangting = q.stocks(stock_list)
    data = []
    '''
    for key,value in stockinfo.items():
        try:
            infoLiutong = (stockinfo[key]['code'],stockinfo[key]['流通市值'])
            data.append(infoLiutong)

        except Exception as e:
            print(e)
            '''
    for key,value in stockinfo_zhangting.items():
        try:
            infoLiutong = (stockinfo_zhangting[key]['code'],stockinfo_zhangting[key]['流通市值'])
            data.append(infoLiutong)

        except Exception as e:
            print(e)
    #sql_truncat = 'truncat table liutong_from_qq'
    sql = 'insert into liutong_from_qq values(?,?)'
    conn = sqlite3API.get_conn('stock.db')
    #sqlite3API.save(conn,sql_truncat,data)
    sqlite3API.save(conn,sql,data)
    print('getLiutong_from_qq OK!')

if __name__ == '__main__':
    #test_sqlite()
#    getLiutong()
    #getIpoInfo()
    getLiutong_from_qq()
#    test_sqlite()
#    tq_test()