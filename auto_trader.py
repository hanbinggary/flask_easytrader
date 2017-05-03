# -*- coding: utf-8 -*-
import easyquotation
#import json 
import tushare as ts
import datetime
import sqlite3 as lite
import sqlite3API
import easytrader

#法定假日判断
def checkFadingJiari():
    #listTrader()
    return True

#有无可交易股票(true:有)   
def checkTraderNone():
    return True
        
#买卖标的满足差价(4%)的委托量远大于交易量(>5倍)        
def checkTrader():
    return True

#买卖标的满足差价(4%)的委托量远大于交易量(>5倍)        
def autoTrader(code_position,code_min,cha):
    #满足差价(4%)才交易
    if cha <= 4 :
        return
    
    if checkTraderNone() == False:
        return
        
    if checkFadingJiari()==False:
        return
        
    try:
        dic_position = getPosition()
        user = getUser1()
        result_sell = user.sell(code_position, None, amount=dic_position[code_position], entrust_prop='market') 
        result_buy = user.buy(code_min, None, amount=dic_position[code_position], entrust_prop='market') 
        print(result_sell,result_buy)
        
        insertPosition(user.position)
        print('huancang OK!')        
    except Exception as e:
        print(e)

def getUser1():
    user = easytrader.use('yh')

    #user.prepare(user='', password='')
    user.prepare('yh.json')
    return user   

#insert 持仓信息 to sqlite
def insertPosition(position):
    data = []
    for dic in position:
        dicList = []
        dicList.append(dic['买入冻结'])
        dicList.append(dic['交易市场'])
        dicList.append(dic['卖出冻结'])
        dicList.append(dic['参考市价'])
        dicList.append(dic['参考市值'])
        dicList.append(dic['参考成本价'])
        dicList.append(dic['参考盈亏'])
        dicList.append(dic['当前持仓'])
        dicList.append(dic['盈亏比例(%)'])
        dicList.append(dic['股东代码'])
        dicList.append(dic['股份余额'])
        dicList.append(dic['股份可用'])
        dicList.append(dic['证券代码'])
        dicList.append(dic['证券名称'])
        data.append(dicList)
    sql = 'insert into chicang values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    conn = sqlite3API.get_conn('stock.db')

    sqlite3API.truncate(conn,'chicang')
    sqlite3API.save(conn,sql,data)
    print('getLiutong_from_qq OK!')
    print (data)

#get 持仓信息 from sqlite
def getPosition():

    conn = sqlite3API.get_conn('stock.db')

    sql_tid='''
        select code,gufen_keyong from chicang ;
        '''
    info_tid=sqlite3API.fetchmany(conn,sql_tid)
#    print(info_tid)
    dic = dict()
    stock_list=[]
    for info_temp in info_tid:
        dic[info_temp[0]] = str(info_temp[1])
        stock_list.append(info_temp[0])
#    print('OK' if '6013192' in dic.keys() else '')
#    print(dic.keys())
    return dic
    
if __name__ == '__main__':
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
      {'买入冻结': 1,
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
      '证券代码': '601392',
      '证券名称': '工商银行1'}]
#    insertPosition(position)
    getPosition()