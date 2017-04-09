from flask import render_template
from flask import Flask
import requests
import easyquotation
import json 
import tushare as ts
import datetime
import sqlite3 as lite
import sqlite3API

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/post/')
@app.route('/hello/post/')
@app.route('/post/<stock>')
def post_test(stock='sz000001'):
    proxies = {
        'http':'http://1:1@10.88.42.18:8080',
        'https':'http://1:1@10.88.42.18:8080' 
    }
    proxies_xx = {
        'http':'http://1:1@10.160.192.3:8080',
        'https':'http://1:1@10.160.192.3:8080' 
    }
    html = requests.get('http://hq.sinajs.cn/?format=text&list=%s' % stock,proxies=proxies)
    return render_template('post_test.html',stockinfo=html.text)

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/post_stock/<stock>')
def post_stock(stock='sz000001'):
    proxies = {
        'http':'http://1:1@10.88.42.18:8080',
        'https':'http://1:1@10.88.42.18:8080' 
    }
    proxies_xx = {
        'http':'http://1:1@10.160.192.3:8080',
        'https':'http://1:1@10.160.192.3:8080' 
    }
    html = requests.get('http://hq.sinajs.cn/?format=text&list=%s' % stock,proxies=proxies)
    return html.text

@app.route('/hello/ipoinfo/')
@app.route('/ipoinfo/')
def getIpoInfo(stock='000001'):
    
    try:
        #上市日期取得
        df = (ts.get_stock_basics())
        cnx = lite.connect('stock.db')
        df.to_sql('stock_info',con=cnx,flavor='sqlite', if_exists='append')
        return '上市日期取得成功'
    except:
        return '上市日期取得失败'

@app.route('/qq/<stock>')
@app.route('/hello/qq/')
@app.route('/qq/')
def tq_test(stock='000001'):
    q = easyquotation.use('qq')
#    print (time.time())
#    print (q.stocks(['000001','000002','000005', '162411']))
#    print (time.time())
    stock_list=['002858','603041','002857','603388','603178','002816','603031','603701','603991','002806','603319','002796','603090','603038','603990','603029','002800','603908','002810','002837','002835','603738','002805','603960','603266','603037','603819','603633','603887','002856','603033','603663','002830','603637','603089','603032','002808']
    stockinfo,stockinfo_zhangting = q.stocks(stock_list)
#    print(stockinfo.get('000001'))
    #json_obj = json.dumps(dict(stock=stockinfo),ensure_ascii=False)
#    print(json_obj)
    temp = sorted(stockinfo.items(), key=lambda d:d[1]['流通市值'])
#    for key ,value in temp:
#        print(value['PB'])
    #print(json.dumps(dict(temp)))
    
    #上市日期取得
    dic = gettimeToMarket(stock_list)

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
            #d1 = datetime.datetime.strptime(str(df.ix[key]['timeToMarket']), '%Y%m%d')
            d1 = datetime.datetime.strptime(dic[key], '%Y%m%d')
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

    return render_template('post_test.html', entries=stockinfo,stockinfo_zhangting=stockinfo_zhangting,stockinfo_sort=temp)

#从本地sqlite取得上市日期
def gettimeToMarket(stock_list):

    conn = sqlite3API.get_conn('stock.db')
    sql_tid ="select code,timeToMarket from stock_info where code in ('" + "','".join(stock_list) + "')"
    info_tid=sqlite3API.fetchmany(conn,sql_tid)
    dic = dict()
    for info_temp in info_tid:
        dic[info_temp[0]] = info_temp[1]
    return dic

if __name__ == '__main__':
    app.run(debug=True)
