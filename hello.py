from flask import render_template
from flask import Flask
import requests

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

if __name__ == '__main__':
    app.run(debug=True)
