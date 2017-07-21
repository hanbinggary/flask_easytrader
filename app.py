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
    
    conn = sqlite3API.get_conn('stock.db')
    sql_tid='select dataTime,lastPrice from t_399006 limit 100'
   
    info_tid=sqlite3API.fetchmany(conn,sql_tid)
    
    info_tid=sqlite3API.fetchmany(conn,sql_tid)
    info_x = []
    info_y = []
    
    for info in info_tid:
        info_x.append(info[0])
        info_y.append(info[1])
    
    return str({"x":info_x,"y":info_y})
    
@app.route('/position/',methods=['GET'])
def getPositionNew():
    return render_template('position.html')

@app.route('/positionhuatai/',methods=['GET'])
def getPositionHuatai():
    
    dic_position = auto_trader.getPositionHuatai()
    
    q = easyquotation.use('qq')
    stockinfo,stockinfo_zhangting = q.stocks(list(dic_position.keys()))
    #合并
    dictMerged=stockinfo.copy()
    dictMerged.update(stockinfo_zhangting)
    
    #按流通市值排序
    temp = sorted(dictMerged.items(), key=lambda d:d[1]['涨跌幅'])
    
    #总持仓市值
    allPosition = 0.0
    #总盈亏
    allYingkui = 0.0
    #今日盈亏
    todayYingkui = 0.0
    
    for key,value in dictMerged.items():
        try:
            #股数
            gushu = dic_position[key][0]
            #成本价
            chengben = dic_position[key][1]
            #now
            now = dictMerged[key]['now']
            #持仓市值
            chicang = round(gushu * dictMerged[key]['now'],2)
            #盈亏
            yingkui = round(gushu * dictMerged[key]['涨跌'],2)
            
            dictMerged[key]['股数']=gushu
            dictMerged[key]['持仓市值']=chicang
            dictMerged[key]['盈亏']=yingkui
            dictMerged[key]['总盈亏']=round((now-chengben)*gushu,2)
            dictMerged[key]['总盈亏(%)']=str(round((now/chengben-1)*100,2)) + '%'
            allPosition += chicang
            allYingkui += round((now-chengben)*gushu,2)
            todayYingkui += yingkui
            
        except:
            pass
    #总盈亏(%)
    allYingkui_1 = round(allYingkui/(allPosition-allYingkui)*100,2)
    #今日盈亏(%)
    todayYingkui_1 = round(todayYingkui/(allPosition-todayYingkui)*100,2)

    return render_template('position_huatai.html', \
                        stockinfo_sort=temp, \
                        allPosition = allPosition, \
                        allYingkui = '%s (%s)' % (str(allYingkui),str(allYingkui_1)+'%'), \
                        todayYingkui = '%s (%s)' % (str(todayYingkui),str(todayYingkui_1)+'%'))

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

