# -*- coding: utf-8 -*-
import os
import smtplib  
from email.mime.text import MIMEText  

mail_host="smtp.139.com"  #设置服务器
mail_user=os.environ['mailfrom'] if os.environ['mailfrom'] else ''   #用户名
mail_pass=os.environ['mailfrompassword'] if os.environ['mailfrompassword'] else ''   #口令 
mail_postfix="139.com"  #发件箱的后缀
mail_to =os.environ['mailto'] if os.environ['mailto'] else ''
  
def send_mail(sub,content,to_list=[mail_to]):  
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