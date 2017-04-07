from flask import render_template
from flask import Flask
import requests
import easyquotation
import json 

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
	#最小流通市值取得
    min_liutong = min(stockinfo.items(), key=lambda d:d[1]['流通市值'])[1]['流通市值']
	#计算流通市值差
    for key,value in stockinfo.items():
        stockinfo[key]['cha'] = round((float(stockinfo[key]['流通市值'])/float(min_liutong) - 1)*100,2)
    return render_template('post_test.html', entries=stockinfo,stockinfo_zhangting=stockinfo_zhangting,stockinfo_sort=temp)

if __name__ == '__main__':
    app.run(debug=True)
