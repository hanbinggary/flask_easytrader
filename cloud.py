# coding: utf-8

from leancloud import Engine
from leancloud import LeanEngineError
#import requests
from app import app
#import time
import app as app_hello
#import sqlite3API

engine = Engine(app)

@engine.define
def hello(**params):
    if 'name' in params:
        return 'Hello, {}!'.format(params['name'])
    else:
        return 'Hello, LeanCloud!'
    
@engine.define
def getHangqingFromQQ():
    app_hello.getHangqingFromQQ()

