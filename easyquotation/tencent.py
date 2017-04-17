# coding:utf8
import re
from datetime import datetime

from .basequotation import BaseQuotation


class Tencent(BaseQuotation):
    """腾讯免费行情获取"""
    stock_api = 'http://qt.gtimg.cn/q='
    grep_stock_code = re.compile(r'(?<=_)\w+')
    max_num = 60

    def format_response_data(self, rep_data, prefix=False):
        stocks_detail = ''.join(rep_data)
        stock_details = stocks_detail.split(';')
        stock_dict = dict()
        stock_dict_zhangting = dict()#涨停板
        
        for stock_detail in stock_details:
            stock = stock_detail.split('~')
            if len(stock) <= 49:
                continue
            stock_code = self.grep_stock_code.search(stock[0]).group() if prefix else stock[2]

            #css设定用
            #损耗大于0.2%时，标红
            sunhao = round((float(stock[19])/float(stock[9])-1)*100,2) if float(stock[9]) > 0.0 else 0.0
            sunhao_css = 'font-green-bold' if sunhao >= 0.2 else ''

            #上市天数<50时，标红加粗

            #stock_dict[stock_code] = {
            temp_item = {
                'name': stock[1],
                'code': stock_code,
                'now': float(stock[3]),
                'close': float(stock[4]),
                'open': float(stock[5]),
                'volume': float(stock[6]) * 100,
                'bid_volume': int(stock[7]) * 100,
                'ask_volume': float(stock[8]) * 100,
                'bid1': float(stock[9]),
                'bid1_volume': int(stock[10]) * 100,
                'bid2': float(stock[11]),
                'bid2_volume': int(stock[12]) * 100,
                'bid3': float(stock[13]),
                'bid3_volume': int(stock[14]) * 100,
                'bid4': float(stock[15]),
                'bid4_volume': int(stock[16]) * 100,
                'bid5': float(stock[17]),
                'bid5_volume': int(stock[18]) * 100,
                'ask1': float(stock[19]),
                'ask1_volume': int(stock[20]) * 100,
                'ask2': float(stock[21]),
                'ask2_volume': int(stock[22]) * 100,
                'ask3': float(stock[23]),
                'ask3_volume': int(stock[24]) * 100,
                'ask4': float(stock[25]),
                'ask4_volume': int(stock[26]) * 100,
                'ask5': float(stock[27]),
                'ask5_volume': int(stock[28]) * 100,
                '损耗': str(sunhao) + '%',
                'sunhao_css': sunhao_css,
                '最近逐笔成交': stock[29],  # 换成英文
                'datetime': str(datetime.strptime(stock[30], '%Y%m%d%H%M%S'))[10:],
                '涨跌': float(stock[31]),  # 换成英文
                '涨跌(%)': str(float(stock[32])) + '%',  # 换成英文
                '涨跌_css': 'font-red' if float(stock[32]) > 0.0 else 'font-green',  # 涨红跌绿
                'high': float(stock[33]),
                'low': float(stock[34]),
                '价格/成交量(手)/成交额': stock[35],  # 换成英文
                '成交量(手)': int(stock[36]) * 100,  # 换成英文
                '成交额': float(stock[37]),  # 成交额(万)
                'turnover': float(stock[38]) if stock[38] != '' else None,
                'PE': float(stock[39]) if stock[39] != '' else None,
                'unknown': stock[40],
                'high_2': float(stock[41]),  # 意义不明
                'low_2': float(stock[42]),  # 意义不明
                '振幅': float(stock[43]),  # 换成英文
                '流通市值': float(stock[44]) if stock[44] != '' else 0.0,  # 换成英文
                'cha': 0,  # 市值差
                'cha_sunhao': 0,  # 去损耗市值差
                'ipo_date_num': 0,  # 上市天数
                'ipo_date_num_css': 0,  # 上市天数
                'ask1_num': round(float(stock[19])*int(stock[20])/100,2),  # 卖一委托额(万)
                'ask1_num_css': 'font-red' if round(float(stock[19])*int(stock[20])/100,2) <= 1 else '',  # 卖一委托额(万)css
                'bid1_num': round(float(stock[9])*int(stock[10])/100,2),  # 买一委托额(万)
                'bid1_num_css': 'font-red' if round(float(stock[9])*int(stock[10])/100,2) <=1 else '',  # 买一委托额(万)css
                '总市值': float(stock[45]) if stock[44] != '' else None,  # 换成英文
                'PB': float(stock[46]),
                '涨停价': float(stock[47]),  # 换成英文
                '跌停价': float(stock[48])  # 换成英文
            }
            if (float(stock[47]) == float(stock[3]) or float(stock[3])==0.0 or float(stock[32])>10):
                #涨停板
                stock_dict_zhangting[stock_code] = temp_item
            elif (float(stock[3])>0.0):
                #现价0.0时，表示停牌
                stock_dict[stock_code] = temp_item
        return stock_dict,stock_dict_zhangting
