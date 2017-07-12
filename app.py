from flask import render_template
from flask import Flask
from flask import request
import requests
import easyquotation
#import json 
#import tushare as ts
import datetime
#import sqlite3 as lite
import sqlite3API
import easytrader
import auto_trader

app = Flask(__name__)
app.config.update(
    PREFERRED_URL_SCHEME='https'
)

@app.route('/')
def hello(name=None):
    
    return render_template('hello.html', position=auto_trader.getAllPositionFromSqlite())

@app.route('/ipoinfo/')
def getIpoInfo(stock='000001'):
    pass
#    try:
#        #上市日期取得
#        df = (ts.get_stock_basics())
#        cnx = lite.connect('stock.db')
#        df.to_sql('stock_info',con=cnx,flavor='sqlite', if_exists='replace')
#        return 'get ipo OK'
#    except:
#        return 'get ipo error'

@app.route('/buy/',methods=['POST'])
def buy():
    try:
        num = request.form['num']
        stockno = request.form['stockno']
        price = request.form['price']

        if len(stockno) != 6:
            return 'tockno error. stockno:' + stockno
        
        user = getUser()
        result=dict()
        
        result = user.buy(stockno, price, amount=num, entrust_prop='market')   
        
#        print(result)
        return dictToString(result)
        
        #return "stock:" + stockno + ",num:" + num 
    except Exception as e:
        #print(e)
        return e
        
@app.route('/hangqing/<stockno>',methods=['GET'])
def hangqing(stockno):
    
    sz_sh = 'sz'
    if (stockno[:1]=='6' or stockno[:1]=='5'):
        sz_sh = 'sh'
        
    url = 'http://qt.gtimg.cn/q=%s' % (sz_sh + stockno)
    proxies = {
        'http':'http://1:1@10.88.42.18:8080',
        'https':'http://1:1@10.88.42.18:8080' 
    }
    html = requests.get(url,proxies=proxies)
    stock = html.text.split('~')
    stockname = ''
    if (len(stock) > 1):
        stockname = stock[1]
    return render_template('stock.html', stockno=stockno,stockname = stockname )
        
@app.route('/hangqingsub/<stockno>',methods=['GET'])
def hangqingsub(stockno):
    proxies = {
        'http':'http://1:1@10.88.42.18:8080',
        'https':'http://1:1@10.88.42.18:8080' 
    }
    url='https://app.leverfun.com/timelyInfo/timelyOrderForm?stockCode=%s' % stockno
    html = requests.get(url,proxies=proxies)
    return html.text

def getUser():
    user = easytrader.use('yh')

    #user.prepare(user='', password='')
    user.prepare('yh.json')
    return user
    
def dictToString(sample_dic):
    result_str = []
    for key, value in sample_dic.items():
        result_str.append("'%s':'%s'" % (key, value))
    return ','.join(result_str)
    
@app.route('/sell/',methods=['POST'])
def sell():
    try:
        num = request.form['num']
        stockno = request.form['stockno']
        price = request.form['price']

        if len(stockno) != 6:
            return 'tockno error. stockno:' + stockno

        user = getUser()
        result = user.sell(stockno, price, amount=num, entrust_prop='market')
        return dictToString(result)

    except Exception as e:
        #print(e)
        return e
    
@app.route('/toChiyou/',methods=['POST'])
def toChiyou():
    try:
        code = request.form['code']
        name = request.form['name']
        print(code)

        sql = 'insert into chicang (gufen_keyong,code,name) values(100,?,?)'
        conn = sqlite3API.get_conn('stock.db')
    
#        sqlite3API.truncate(conn,'chicang')
        data = [[code,name]]
        sqlite3API.save(conn,sql,data)

        return 'insert chicang OK'

    except Exception as e:
        #print(e)
        return e
    
@app.route('/delChiyou/',methods=['POST'])
def delChiyou():
    try:
        code = request.form['code']

        sql = 'delete from chicang where code=?'
        conn = sqlite3API.get_conn('stock.db')
    
#        sqlite3API.truncate(conn,'chicang')
        data = [[code]]
        sqlite3API.save(conn,sql,data)

        return 'delete %s OK' % code

    except Exception as e:
        #print(e)
        return e

@app.route('/getminline/<stockno>',methods=['GET'])
def getminline(stockno):
    x = ["11:01","11:02","11:03","11:04","11:05","11:06","11:07","11:08","11:09","11:10","11:11","11:12","11:13","11:14","11:15","11:16","11:17","11:18","11:19","11:20","11:21","11:22","11:23","11:24","11:25","11:26","11:27","11:28","11:29","11:30","13:01","13:02","13:03","13:04","13:05","13:06","13:07","13:08","13:09","13:10","13:11","13:12","13:13","13:14","13:15","13:16","13:17","13:18","13:19","13:20","13:21","13:22","13:23","13:24","13:25","13:26","13:27","13:28","13:29","13:30"]
    y = [1.08,5.69,3.23,7.28,2.41,9.12,9.46,7.26,0.75,5.64,1.18,4.84,6.43,3.39,4.73,7.3,1.34,0.7,7.07,9.56,8.21,8.77,1.67,8.11,8.57,4.62,4.18,5.48,4.64,8.56,0.88,3.72,0.77,1.46,7.2,9.94,9.07,9.11,7.24,2.59,1.97,2.09,7,1.41,0.92,9.9,4.11,5.84,8.66,7.85,4.37,4.72,5.89,8.79,8.53,3.65,6.69,2.74,6.4,9.79]
    return str({"x":x,"y":y})
#    return '{"x":%s,"y":%s}' % (x,y)
    
#批量取得最新行情 高频数据
@app.route('/qq/')
def getHangqingFromQQ():
    
    q = easyquotation.use('qq')

    #取上市300天内的最小流通市值 top 40
    dic,stock_list = gettimeToMarket()

    #取得最新行情 from qq
    stockinfo,stockinfo_zhangting = q.stocks(stock_list)

    #按流通市值排序
    temp = sorted(stockinfo.items(), key=lambda d:d[1]['流通市值'])

    #最小流通市值取得
    min_liutong = min(stockinfo.items(), key=lambda d:d[1]['流通市值'])[1]
    
    #get Position
    dic_position = auto_trader.getPosition()
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
            ipo_date_num = (datetime.datetime.now()-d1).days
            stockinfo[key]['ipo_date_num'] = ipo_date_num if ipo_date_num > 50 else str(ipo_date_num) + ' 天'
            stockinfo[key]['ipo_date_num_css'] = 'font-red-bold' if ipo_date_num <= 50 else ''
            #该股为持仓股时，判断是否需要调仓
            #if key in dic_position.keys():
                #auto_trader.autoTrader(stockinfo[key],min_liutong,round((liutong_sunhao/min_liutong_sunhao - 1)*100,3))
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
    sql_tid='''
        select stock_info.code,stock_info.timeToMarket from liutong_from_qq 
        inner join stock_info on
        liutong_from_qq.code = stock_info.code
        where liutong_from_qq.liutong<13 and substr(liutong_from_qq.code,1,1) != '3' 
        and substr(stock_info.timeToMarket,1,4) || '-' || substr(stock_info.timeToMarket,5,2) || '-' || substr(stock_info.timeToMarket,7,2) > date('now','-270 days')
        order by liutong_from_qq.liutong 
        limit 40;
        '''
    #union all XXX 持仓股
        
    info_tid=sqlite3API.fetchmany(conn,sql_tid)
    dic = dict()
    stock_list=[]
    for info_temp in info_tid:
        dic[info_temp[0]] = str(info_temp[1])
        stock_list.append(info_temp[0])
    
    return dic,stock_list

if __name__ == '__main__':
    app.run(debug=True)

