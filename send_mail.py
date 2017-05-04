# -*- coding: utf-8 -*-

import smtplib  
from email.mime.text import MIMEText  
mail_host="smtp.139.com"  #设置服务器
mail_user="XXX@139.com"    #用户名
mail_pass=""   #口令 
mail_postfix="139.com"  #发件箱的后缀
  
def send_mail(sub,content,to_list=['@126.com']):  
    me="hello"+"<"+mail_user+"@"+mail_postfix+">"  
    msg = MIMEText(content,_subtype='plain',_charset='gb2312')  
    msg['Subject'] = sub  
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  
    try:  
        server = smtplib.SMTP()  
        server.connect(mail_host)  
        server.login(mail_user,mail_pass)  
        server.sendmail(me, to_list, msg.as_string())  
        server.close()  
        return True  
    except Exception as e:  
        print (e)  
        return False  
if __name__ == '__main__':  
    if send_mail("hello","hello world！"):  
        print ("发送成功"  )
    else:  
        print ("发送失败"  )