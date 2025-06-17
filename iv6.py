import json
import hashlib
import subprocess
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
        result = subprocess.check_output(['/usr/sbin/ifconfig'], universal_newlines=True)
        interfaces = result.split('\n\n')  # 按空行分割不同的网络接口信息
        for interface in interfaces:
            lines = interface.splitlines()
            if len(lines) > 0:
                interface_name = lines[0].split(':')[0]  # 提取网卡名称
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
        except Exception as e:
            print(f"写入文件时出错: {e}")
    else:
        print("无法获取 IPv6 地址，未写入文件。")

if __name__ == "__main__":
    path = '/home/pi/sendipv6address/'
    old_file_name = path+ 'local_ipv6_old.json'
    new_file_name = path+ "local_ipv6.json"
    write_ipv6_to_json(new_file_name)
    if calculate_md5(old_file_name) != calculate_md5(new_file_name):
        subprocess.run(['/usr/bin/cat', old_file_name])
        subprocess.run(['/usr/bin/cat', new_file_name])
        subprocess.run(['/usr/bin/mv', new_file_name, old_file_name])
    else:
        subprocess.run(['/usr/bin/rm', new_file_name])
        print('IP没有变化！')

