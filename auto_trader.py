# -*- coding: utf-8 -*-
#import easyquotation
#import json 
#import tushare as ts
import datetime
#import sqlite3 as lite
import sqlite3API
import easytrader
import time
from send_mail import send_mail

#法定假日判断
def checkFadingJiari(str_time = str(datetime.datetime.now())[:10]):
    conn = sqlite3API.get_conn('stock.db')

    sql_tid='''
        select isOpen from trade_calender where calendarDate = '%s';
        '''
    info_tid=sqlite3API.fetchmany(conn,sql_tid % str_time)
    if info_tid and info_tid[0][0] ==1:
        return True
    else :
        return False

#有无可交易股票(true:有)   
def checkTraderNone(code_position):
    conn = sqlite3API.get_conn('stock.db')

    sql_tid='''
        select gufen_keyong from chicang where code = '%s';
        '''
    info_tid=sqlite3API.fetchmany(conn,sql_tid % code_position)
    if info_tid and info_tid[0][0] > 0:
        return True
    else :
        return False

#交易时间判断
def checkTradeTime(str_time):
    if str_time >= '09:30' and str_time < '11:29':
        return True
        
    #闭市前几分钟无法看到五档行情，不做交易
    if str_time >= '13:00' and str_time < '14:26':
        return True
    
    return False
    
#买卖标的满足差价(4%)的委托量远大于交易量(>5倍)        
def autoTrader(position_info,min_liutong,cha):
    code_position = position_info['code']
    #满足差价(4%)才交易
    if cha <= 4 :
        print ('cha %s' % cha)
        return
        
    if checkFadingJiari()==False:
        print('isOpen = False')
        return
    
    if checkTraderNone(code_position) == False:
        print('gufen_keyong = 0')
        return
    
    if checkTradeTime(min_liutong['datetime'][1:6]) == False:
        print('非交易时间%s' % min_liutong['datetime'])
        return
    return    
    try:
        dic_position = getPosition()
        user = getUser()
        position = user.position
        for item in position:
            if item['证券代码'] == code_position and item['股份可用'] == 0:
                print ('无可卖股份')
                return
                
        result_sell = user.sell(code_position, '1000', amount=dic_position[code_position], entrust_prop='market') 
        time.sleep(0.2)
        result_buy = user.buy(min_liutong['code'], '1', amount=dic_position[code_position], entrust_prop='market') 
        print(result_sell,result_buy)
        
        insertPosition(user.position)
        message_ok = 'sell %s buy %s amount %s' % (code_position,min_liutong['code'],dic_position[code_position])
        send_mail('huancang OK',message_ok)
        print('huancang OK!',message_ok)        
    except Exception as e:
        send_mail('error trade',str(e))
        print(e)

def getUser():
    user = easytrader.use('yh')

    #user.prepare(user='', password='')
    user.prepare('yh.json')
    return user   

#登录交易记录
def insertTradeHistory(position_info,min_liutong):
    sql = 'insert into XXXXXXXXX values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    conn = sqlite3API.get_conn('stock.db')
    data = []
    data.append(editStockInfo(position_info,'S'))
    data.append(editStockInfo(min_liutong,'B'))
    sqlite3API.truncate(conn,'chicang')
    sqlite3API.save(conn,sql,data)
    print('insertTradeHistory OK!')
    print (data)

#备份交易时的行情快照
def editStockInfo(stock_info,flg='B'):
    result = []
    result.append(flg)
    result.append(stock_info['name'])
    result.append(stock_info['code'])
    result.append(stock_info['now'])
    result.append(stock_info['close'])
    result.append(stock_info['open'])
    result.append(stock_info['volume'])
    result.append(stock_info['bid_volume'])
    result.append(stock_info['ask_volume'])
    result.append(stock_info['bid1'])
    result.append(stock_info['bid1_volume'])
    result.append(stock_info['bid2'])
    result.append(stock_info['bid2_volume'])
    result.append(stock_info['bid3'])
    result.append(stock_info['bid3_volume'])
    result.append(stock_info['bid4'])
    result.append(stock_info['bid4_volume'])
    result.append(stock_info['bid5'])
    result.append(stock_info['bid5_volume'])
    result.append(stock_info['ask1'])
    result.append(stock_info['ask1_volume'])
    result.append(stock_info['ask2'])
    result.append(stock_info['ask2_volume'])
    result.append(stock_info['ask3'])
    result.append(stock_info['ask3_volume'])
    result.append(stock_info['ask4'])
    result.append(stock_info['ask4_volume'])
    result.append(stock_info['ask5'])
    result.append(stock_info['ask5_volume'])
    result.append(stock_info['损耗'])
    result.append(stock_info['sunhao_css'])
    result.append(stock_info['最近逐笔成交'])
    result.append(stock_info['datetime'])
    result.append(stock_info['涨跌'])
    result.append(stock_info['涨跌(%)'])
    result.append(stock_info['high'])
    result.append(stock_info['low'])
    result.append(stock_info['价格/成交量(手)/成交额'])
    result.append(stock_info['成交量(手)'])
    result.append(stock_info['成交额'])
    result.append(stock_info['turnover'])
    result.append(stock_info['PE'])
    result.append(stock_info['unknown'])
    result.append(stock_info['high_2'])
    result.append(stock_info['low_2'])
    result.append(stock_info['振幅'])
    result.append(stock_info['流通市值'])
    result.append(stock_info['cha'])
    result.append(stock_info['cha_sunhao'])
    result.append(stock_info['ipo_date_num'])
    result.append(stock_info['总市值'])
    result.append(stock_info['PB'])
    result.append(stock_info['涨停价'])
    result.append(stock_info['跌停价'])
    return result
    
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

def getPositionFromYinhe():
    user = getUser()
    position = user.position
    return position
    
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
#    print(time.time())
#    insertPosition(getPositionFromYinhe())
#    getPosition()
    print(time.time())
    print(checkTraderNone('601398'))
    print(time.time())
