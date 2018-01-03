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
    if str_time >= '13:00' and str_time < '14:57':
        return True
    
    return False
    
#买卖标的满足差价(4%)的委托量远大于交易量(>5倍)        
def autoTrader(position_info,min_liutong,cha):
    code_position = position_info['code']
    #满足差价(4%)才交易
    if cha <= 3 :
        print ('cha %s' % cha)
        return
        
    if checkFadingJiari()==False:
        print('isOpen = False')
        return
    
    if checkTraderNone(code_position) == False:
        print('gufen_keyong = 0')
        return
    
    if checkTradeTime(min_liutong['datetime'][1:6]) == False:
        print('not trade time %s' % min_liutong['datetime'])
        return

    try:
        dic_position = getPosition()
        user = getUser()
        '''
        position = user.position
        for item in position:
            if item['证券代码'] == code_position and item['股份可用'] == 0:
                print ('keyong_gufen == 0')
                return
        '''     
        result_sell = user.sell(code_position, '1000', amount=dic_position[code_position], entrust_prop='market') 
        time.sleep(1)
        result_buy = user.buy(min_liutong['code'], '1', amount=dic_position[code_position], entrust_prop='market') 
        #print(result_sell,result_buy)
        time.sleep(1)
        insertPosition(user.position)
        insertTradeHistory(position_info,min_liutong)
        message_ok = 'sell %s buy %s amount %s' % (code_position,min_liutong['code'],dic_position[code_position])
        send_mail('huancang OK',message_ok)
        print('*' * 50)        
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
    sql = 'insert into trade_history values(' + ('?,'*47) + "?,datetime('now'))"
    conn = sqlite3API.get_conn('stock.db')
    data = []
    data.append(editStockInfo(position_info,'S'))
    data.append(editStockInfo(min_liutong,'B'))
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
    result.append(stock_info['datetime'])
    result.append(stock_info['涨跌'])
    result.append(stock_info['涨跌(%)'])
    result.append(stock_info['high'])
    result.append(stock_info['low'])
    result.append(stock_info['成交量(手)'])
    result.append(stock_info['成交额'])
    result.append(stock_info['turnover'])
    result.append(stock_info['PE'])
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
    print('insertPosition OK!')
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
def getAllPositionFromSqlite():

    conn = sqlite3API.get_conn('stock.db')

    sql_tid='''
        select mairu_dongjie,jiaoyi_shichang,maichu_dongjie,shijia,shizhi,chengbenjia,yingkui,tangqian_chicang,yingkui_bili,gudong_daima,gufen_yue,gufen_keyong,code,name from chicang ;
        '''
    info_tid=sqlite3API.fetchmany(conn,sql_tid)
#    print(info_tid)
    list_dic=[]
#    dic = dict()
    for info_temp in info_tid:
        temp_item = {
            '买入冻结': info_temp[0],
            '交易市场': info_temp[1],
            '卖出冻结': info_temp[2],
            '参考市价': info_temp[3],
            '参考市值': info_temp[4],
            '参考成本价': info_temp[5],
            '参考盈亏': info_temp[6],
            '当前持仓': info_temp[7],
            '盈亏比例(%)': info_temp[8],
            '股东代码': info_temp[9],
            '股份余额': info_temp[10],
            '股份可用': info_temp[11],
            '证券代码': info_temp[12],
            '证券名称': info_temp[13]
        }
#        dic[info_temp[12]]=temp_item
#        print(temp_item)
        list_dic.append(temp_item)
    return list_dic

#取得华泰真实的持仓，非次新
def getPositionHuatai():

    conn = sqlite3API.get_conn('stock.db')

    sql_tid='''
        select * from position ;
        '''
    info_tid=sqlite3API.fetchmany(conn,sql_tid)
    
    dic = dict()

    for info_temp in info_tid:
        dic[info_temp[0]] = [info_temp[1],info_temp[2],info_temp[3],info_temp[4],info_temp[5]]

    return dic

#插入华泰真实的持仓，非次新
def insertPositionHuatai(data):

    conn = sqlite3API.get_conn('stock.db')

    sql_tid='''
        insert into position values(?,?);
        '''
    sqlite3API.save(conn,sql_tid,data)

#删除华泰真实的持仓，非次新
def delPositionHuatai(data):

    conn = sqlite3API.get_conn('stock.db')

    sql_tid='''
        delete from position where code=?;
        '''
    sqlite3API.save(conn,sql_tid,data)

def getPositionFromYinhe():
    user = getUser()
    position = user.position
    return position

def get_ipo_info():
    user = getUser()
    df_today_ipo, df_ipo_limit = user.get_ipo_info()
    print (df_today_ipo)
    for i in range(len(df_today_ipo)):
        code = df_today_ipo.ix[i]['代码']
        price = df_today_ipo.ix[i]['价格']
        amount = df_today_ipo.ix[i]['账户额度']
        result = user.buy(code,price,amount=amount)
        print(result)
    
if __name__ == '__main__':

    dic = getPosition()
    print(dic)
    print(dic.keys())
    list1= [1,2]
    list2 = list(set(dic.keys())|set(list1))
    print(list2)