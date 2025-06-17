#!/usr/bin/python 
#-*- coding:utf-8 -*-
import json
import smtplib 
from email.mime.text import MIMEText 
import sys  
mail_host = 'smtp.163.com'   #smtp地址如果不知可以百度如“163邮箱smtp地址”
mail_user = 'abc@163.com'           #此账号密码是用来给人发送邮件的
mail_user_name= 'Chaos'           #此账号密码是用来给人发送邮件的
mail_pass = 'abc123'           #此账号密码是用来给人发送邮件的
mail_postfix = '163.com'   #邮箱地址，smtp地址删去smtp字符如“163.com”
  
def send_mail(to_list,subject,content): 
    me = mail_user+"<"+mail_user+">"
    content_str = "\n".join([f"{iface}: {addr}" for item in content for iface, addr in item.items()])
    msg = MIMEText(content_str) 
    msg['Subject'] = subject 
    msg['From'] = me 
    msg['to'] = ','.join(to_list) 
    try: 
        s = smtplib.SMTP_SSL(mail_host)
        s.login(mail_user,mail_pass) 
        print(me)
        s.sendmail(me,to_list,msg.as_string()) 
        s.close() 
        return True
    except Exception as e: 
        print(e) 
        return False
def read_txt_file_to_list(file_path):
    print(file_path)
    lines = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()  # 读取文件的所有行，并存储在列表中
            return lines
    except FileNotFoundError:
        print('文件{file_path}不存在，请检查文件路径是否正确。')
    except Exception as e:
        print("读取文件时发生错误: {e}")
def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)  # 使用 json.load 函数将文件内容解析为 Python 对象
            return data
    except FileNotFoundError:
        print("文件 {file_path} 未找到，请检查文件路径是否正确。")
    except json.JSONDecodeError:
        print("文件 {file_path} 不是有效的 JSON 格式，请检查文件内容。")
    except Exception as e:
        print("读取文件时发生错误: {e}")

if __name__ == "__main__": 
    file = read_json_file('/home/pi/sendipv6address/sendmail.json')
    #file = read_json_file(sys.argv[1])
    print(file)
    send_mail(file.get('address'),file.get('subject'),file.get('contain'))
    #send_mail(sys.argv[1], sys.argv[2], sys.argv[3])
