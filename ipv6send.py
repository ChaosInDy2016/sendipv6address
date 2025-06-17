import smtplib 
from email.mime.text import MIMEText 
import sys  
import json
import hashlib
import subprocess
PATH_DATA = '/home/pi/sendipv6address/'
PATH_SBIN = '/usr/sbin/'
PATH_BIN = '/usr/bin/'
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
        s.sendmail(me,to_list,msg.as_string()) 
        s.close() 
        return True
    except Exception as e: 
        print(e) 
        return False

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

def update_json_file(file_path, new_content):
    try:
        data = read_json_file(file_path)
        data['contain'] = new_content
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        return data
    except Exception as e:
        print(f"读取或写入文件时发生错误: {e}")
        return []

def calculate_md5(file_path):
    md5 = hashlib.md5()
    try:
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(65536)  # 分块读取文件，避免大文件读取时内存问题
                if not data:
                    break
                md5.update(data)
                return md5.hexdigest()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
        return None
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return None

def get_ipv6_addresses():
    network_info = {}
    try:
        ipv6_lines = []
        result = subprocess.check_output([PATH_SBIN + 'ifconfig'], universal_newlines=True)
        interfaces = result.split('\n\n')  # 按空行分割不同的网络接口信息
        for interface in interfaces:
            lines = interface.splitlines()
            if len(lines) > 0:
                interface_name = lines[0].split(':')[0]  # 提取网卡名称
                if interface_name != 'eth0':
                    continue
                for line in lines:
                    if "inet6" in line:  # 只提取包含 inet6 的行
                        parts = line.split()
                        if parts[1][0] != 'f' and parts[1][0] != ':' :
                            ipv6_lines.append({interface_name: parts[1]})
        return ipv6_lines
    except subprocess.CalledProcessError as e:
        print(f"执行 ifconfig 命令时出错: {e}")
        return None

def write_ipv6_to_json(file_path):
    network_info = get_ipv6_addresses()
    if network_info:
        try:
            with open(file_path, 'w') as file:
                json.dump(network_info, file, indent=4)
                return network_info
        except Exception as e:
            print(f"写入文件时出错: {e}")
            return []
    else:
        print("无法获取 IPv6 地址，未写入文件。")
        return []

if __name__ == "__main__":
    mail_json = PATH_DATA + 'sendmail.json'
    old_file_name = PATH_DATA + 'local_ipv6_old.json'
    new_file_name = PATH_DATA + 'local_ipv6.json'
    infos = write_ipv6_to_json(new_file_name)
    if calculate_md5(old_file_name) != calculate_md5(new_file_name):
        subprocess.run([PATH_BIN + 'cat', old_file_name])
        subprocess.run([PATH_BIN + 'cat', new_file_name])
        subprocess.run([PATH_BIN + 'mv', new_file_name, old_file_name])
        file = update_json_file(mail_json, infos)
        if file:
            send_mail(file.get('address'),file.get('subject'),file.get('contain'))
    else:
        subprocess.run([PATH_BIN + 'rm', new_file_name])
        print('IP没有变化！')
