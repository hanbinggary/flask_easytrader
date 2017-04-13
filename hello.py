from flask import render_template
from flask import Flask
from flask import request
#import requests
import easyquotation
import json 
import tushare as ts
import datetime
import sqlite3 as lite
import sqlite3API
import easytrader

app = Flask(__name__)

@app.route('/')
def hello(name=None):
    #user.position
    position=\
    [{'买入冻结': 0,
  '交易市场': '沪A',
  '卖出冻结': '0',
  '参考市价': 4.71,
  '参考市值': 10362.0,
  '参考成本价': 4.672,
  '参考盈亏': 82.79,
  '当前持仓': 2200,
  '盈亏比例(%)': '0.81%',
  '股东代码': 'xxx',
  '股份余额': 2200,
  '股份可用': 2200,
  '证券代码': '601398',
  '证券名称': '工商银行'},
  {'买入冻结': 0,
  '交易市场': '沪A',
  '卖出冻结': '0',
  '参考市价': 4.71,
  '参考市值': 10362.0,
  '参考成本价': 4.672,
  '参考盈亏': 82.79,
  '当前持仓': 2200,
  '盈亏比例(%)': '0.81%',
  '股东代码': 'xxx',
  '股份余额': 2200,
  '股份可用': 2200,
  '证券代码': '601398',
  '证券名称': '工商银行1'}]
    return render_template('hello.html', name=name,position=position)

@app.route('/ipoinfo/')
def getIpoInfo(stock='000001'):
    
    try:
        #上市日期取得
        df = (ts.get_stock_basics())
        cnx = lite.connect('stock.db')
        df.to_sql('stock_info',con=cnx,flavor='sqlite', if_exists='append')
        return 'get ipo OK'
    except:
        return 'get ipo error'

@app.route('/buy/',methods=['POST'])
def buy():
    try:
        num = request.form['num']
        stockno = request.form['stockno']
        price = '0' #request.form['price','0']

        if len(stockno) != 6:
            return 'tockno error. stockno:' + stockno
        '''
        user = easytrader.use('yh')
        user.prepare(user='', password='')

        if price=='0':
            return user.buy(stockno, amount=num, entrust_prop='market')
        else:
            return user.buy(stockno, price=price, amount=num)
        '''

        return "stock:" + stockno + ",num:" + num 
    except Exception as e:
        print(e)
        return e

@app.route('/sell/',methods=['POST'])
def sell():
    try:
        num = request.form['num']
        stockno = request.form['stockno']
        price = request.form.get['price','0']

        if len(stockno) != 6:
            return 'tockno error. stockno:' + stockno

        user = easytrader.use('yh')
        user.prepare(user='', password='')

        if price=='0':
            return user.sell(stockno, amount=num, entrust_prop='market')
        else:
            return user.sell(stockno, price=price, amount=num)

        #return "stock:" + stockno + ",num:" + num 
    except Exception as e:
        print(e)
        return e

#批量取得最新行情 高频数据
@app.route('/qq/')
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
        except:
            pass

    for key,value in stockinfo_zhangting.items():
        try:
            #上市天数计算
            d1 = datetime.datetime.strptime(dic[key], '%Y%m%d')
            ipo_date_num = (datetime.datetime.now()-d1).days
            stockinfo_zhangting[key]['ipo_date_num'] = ipo_date_num if ipo_date_num > 50 else str(ipo_date_num) + '天'
        except:
            pass

    return render_template('post_test.html', stockinfo_zhangting=stockinfo_zhangting,stockinfo_sort=temp)

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

if __name__ == '__main__':
    app.run(debug=True)

