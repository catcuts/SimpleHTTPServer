#coding = utf8
# -*- coding: utf-8 -*-
''' 
    用法：
            
'''
import os
import re
import sys
import json
import shutil
import subprocess

DEFAULT_NETWORK_CONF = {
    "eth0": {
        "ip": "",
        "gateway": "",
        "netmask": "",
        "dns_prefer": "",
        "dns_alter": "",
    }
}

class RpiController:
    
    path_dhcpcd_conf = "/etc/dhcpcd.conf" # RaspberryPi 网络配置文件路径
    path_resolv_conf = "/etc/resolv.conf" # RaspberryPi DNS 服务器地址存放文件路径
    path_bkup_folder = "/home/pi/bkup"  # 

    def __init__(self, default_network_conf=DEFAULT_NETWORK_CONF):
        self.default_network_conf = default_network_conf
        if not os.path.exists(self.path_bkup_folder):
            try:
                original_umask = os.umask(0)
                os.makedirs(self.path_bkup_folder)
            except:
                os.umask(original_umask)

    def shutdown(self, *args, **kwargs):
        subprocess.Popen("shutdown -h now", shell=True)
     
    def reboot(self, *args, **kwargs):
        subprocess.Popen("shutdown -r now", shell=True)

    def restartNetwork(self, *args, **kwargs):
        subprocess.Popen("sudo /etc/init.d/networking restart", shell=True)

    def changeNetwork(self, device="eth0", ip="", gateway="", netmask="", dns_prefer="", dns_alter="", **kwargs):
        check_error = self.checkNetConf(device, ip, gateway, netmask, dns_prefer, dns_alter)
        if check_error: return check_error

        self.bkupFile(self.path_dhcpcd_conf)

        fp = self.path_dhcpcd_conf
        #  整区匹配 \n[^#]*\s*interface\s(eth0)\s*\n\s*static\sip_address\s*=([^/]*)/(.*)\n\s*static\srouters\s*=(.*)\n\s*(static\sdomain_name_servers\s*=(.*))?\n*
        r_netconf = re.compile("\\n[^#]*interface\\s(" + device + ")\\s*\\n\\s*static\\sip_address\\s*=(.*)/(.*)\\n\\s*static\\srouters\\s*=(.*)\\n\\s*(static\\sdomain_name_servers\\s*=(.*))?\\n*")

        #  分段匹配
        # r_head = re.compile("[^#]interface\\s*(" + dev + ")\\s*")  #  网卡设备
        # r_ip = re.compile("[^#]\\s*(static\\sip_address=.*)")  # ip地址/子网掩码
        # r_gateway = re.compile("[^#]\\s*(static\srouters=.*)")  # 路由器/网关地址
        # r_dns = re.compile("[^#]\\s*(static\\sdomain_name_servers=.*)")  # dns地址

        # 开始 -> 构造 -> 替换/追加 -> 写入 -> 结束
        # 一个生命周期从开始到结束
        # 每个环节都应该是尽量互相独立的，保证低耦合，高可维护，易扩展
        # 如果需要更新某个环节，则不影响其他环节
        # 如果需要加入某个环节，应继续保证与其他环节独立

        if not (ip or netmask or gateway):  # 重置
            new_netconf = ""
        else:  # 非重置
            #  初始化
            line_head = "interface " + device
            line_ipnm = " static ip_address=" + ip + "/" + self.codeNetmask(netmask)
            line_gw = " static routers=" + gateway
            if dns_prefer:
                line_dns = " static domain_name_servers=" + dns_prefer + " " + dns_alter
            else:
                line_dns = ""

            #  构造新配置区
            new_netconf = "\n\n\n" + "\n".join([line_head, line_ipnm, line_gw, line_dns])

        #  新配置替换原配置
        with open(fp, "r") as f:
            fc = f.read()
            m_netconf = re.search(r_netconf, fc)
            if m_netconf:  # 找到原配置则替换
                fc = re.sub(r_netconf, new_netconf, fc)
            else:  # 没有原配置则追加
                fc = fc + new_netconf

        #  写入配置文件
        with open(fp, "w") as f:
            f.write(fc)

        #result = commands.getoutput("sudo ifdown %s && sudo ifup %s" %(self.device,self.device))
        return True

    def resetNetwork(self, device="eth0", *args, **kwargs):
        default = self.default_network_conf.get(device)
        if default is None: return False
        ip = default["ip"]
        gateway = default["gateway"]
        netmask = default["netmask"]
        dns_prefer = default["dns_prefer"]
        dns_alter = default["dns_alter"]
        return self.changeNetwork(device, ip, gateway, netmask, dns_prefer, dns_alter)

    def getNetworkConf(self, *args, **kwargs):  
        # 获取默认网关
        s1 = subprocess.Popen("ip route", shell=True, stdout=subprocess.PIPE)
        lines = s1.communicate()[0].decode().split("\n")
        networkConf = {}
            #finally we can have networkConf like:
                #{
                #   eth0: { gateway:"...", ip:"...", netmask:"..."},
                #   wlan0: { gateway:"...", ip:"...", netmask:"..."},
                #   ...
                #}
        # 获取ip地址、子网掩码、默认网关
        for line in lines: 
            if "default via" in line: #某设备默认网络参数
                m = re.search(r"default\svia\s(\d+\.\d+\.\d+\.\d+)\sdev\s(\w+)\s", line)
                if m: #每一组都是都是必选的，如果匹配到，说明组内都不为空
                    m = list(map(lambda x:x.encode("utf-8"), m.groups()))
                    networkConf[m[1]] = {} #默认网关对一个设备只有一个，所以识别到就是新值
                    networkConf[m[1]]["gateway"] = m[0] #example: { eth0: { gateway: '192.168.8.1'. }, }
        #     elif line:
        #         m = re.search(r"(\d+\.\d+\.\d+\.\d+)(\/\d+)*\sdev\s(\w+)\s", line)
        #         if m: #同上
        #             m = list(map(lambda x:x.encode("utf-8"), m.groups()))
        #             try:
        #                 networkConf[m[2]] #因为这个设备可能已经有一些json了，先试试有没有
        #             except:
        #                 networkConf[m[2]] = {} #没有就赋空
        #             networkConf[m[2]]["ip"] = m[0]
        #             networkConf[m[2]]["netmask"] = self.decodeNetmask(m[1])
        #             dev = m[2]

        #获取dns服务器地址
        dns_prefer = ""
        dns_alter = ""
        with open(self.path_resolv_conf, "r") as f:
            dnsPattern = re.compile("nameserver\s(\d+\.\d+\.\d+\.\d+)\s*\nnameserver\s(\d+\.\d+\.\d+\.\d+)*\s*")
            fc = f.read()
            m = dnsPattern.search(fc)
            if m:
                dns_prefer = m.groups()[0] #这个是必选匹配，如果匹配不到，就根本不会if m
                dns_alter = m.groups()[1] #这个是可选匹配，如果匹配不到，则为""
        #读取文件结束

        # 获取 ip 地址和子网掩码
        s2 = subprocess.Popen("ifconfig", shell=True, stdout=subprocess.PIPE)
        network_drive_info = s2.communicate()[0].decode().split("\n\n")
        # print("\n\t[ meow ]\n%s" % "\n\t\t".join(network_drive_info))
        for i in range(len(network_drive_info)):
        # for i in range(1):
        #     print("\n\t[ wong ]\n%s" % network_drive_info[i])
            # print("\n\t[ woo ]\n%s" % network_drive_info[i].split("\n" + " " * 10)[1])
            _network_drive_info = network_drive_info[i].split("\n")
            m_dev = re.search(r"^(\w+)\b", _network_drive_info[0].strip())
            if m_dev:
                dev = m_dev.group(1)
                networkConf[dev] = {}
                m_netConf = re.search(r"inet\saddr:(\d+\.\d+\.\d+\.\d+).+Mask:(\d+\.\d+\.\d+\.\d+)", _network_drive_info[1].strip())
                if m_netConf:
                    networkConf[dev]["ip"] = m_netConf.group(1)
                    networkConf[dev]["netmask"] = m_netConf.group(2)
                else:
                    networkConf[dev]["ip"] = "unknown"
                    networkConf[dev]["netmask"] = "unknown"
                networkConf[dev]["dns_prefer"] = dns_prefer
                networkConf[dev]["dns_alter"] = dns_alter

        # print("networkConf:\n%s" % json.dumps(networkConf, indent=4))
        return networkConf

    @staticmethod
    def codeNetmask(netmask):
        netmask_parts = netmask.split(".")
        code = 0
        try:
            for part in netmask_parts:
                code += bin(int(part)).count("1")
            code = str(code)
        except:
            code = ""
        return str(code)

    @staticmethod
    def decodeNetmask(code):
        code = code.replace("/","")
        code = "1"*int(code) + "0"*(32-len(code))
        netmask = ""
        if code:
            for i in range(0,4):
                netmask = netmask + str(int(code[i*8:i*8+8], 2)) + "."
        netmask = netmask[:-1]
        return netmask

    @staticmethod
    def checkNetConf(device="eth0", ip="", gateway="", netmask="", dns_prefer="", dns_alter=""):
        # print("meow:\n\t%s\n\t%s\n\t%s" % (ip, gateway, netmask))
        error_format = "error: 无效的格式"
        reset = True if not ip and not gateway and not netmask else False
        if reset:
            return False
        if not (ip and gateway and netmask):  # 三个有一个为空 （三个都为空时，则为重置）
            if not ip: return "error: IP地址不能为空"
            if not gateway: return "error: 网关不能为空"
            if not netmask: return "error: 子网掩码不能为空"
        checkee = '_'.join([ip, gateway, netmask])
        print("checkee: %s" %checkee)
        if not re.search(r"(_*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})_*){3}", checkee):
            return error_format
        if dns_prefer and not re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", dns_prefer):
            return error_format
        if dns_alter and not re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", dns_alter):
            return error_format
        return False

    def bkupFile(self, target_file_path="", bkup_folder_path=""):
        if not os.path.isfile(target_file_path): return
        bkup_folder_path = bkup_folder_path if os.path.isdir(bkup_folder_path) else self.path_bkup_folder
        bkup_file_path = os.path.join(bkup_folder_path, target_file_path + ".bkup")
        if not os.path.exists(bkup_file_path): 
            shutil.copy2(target_file_path, bkup_file_path) 

if __name__ == "__main__":
    """"
    @param: <shutdown>
            <reboot> 
            <getNetworkConf>
            <changeNetwork>, <device>, <ip>, <gateway>, <netmask>, <dns_prefer>, <dns_alter>
            <resetNetwork>, <device>
    """
    command = ""
    try:
        command = sys.argv[1]
    except:
        print("""
        关机:  shutdown
        重启:  reboot
查看网络配置:  getNetworkConf
修改网络配置:  changeNetwork, <device>, <ip>, <gateway>, <netmask>, <dns_prefer>, <dns_alter>
恢复网络配置:  resetNetwork, <device>""")
        exit()

    if command not in ["shutdown", "reboot", "getNetworkConf", "changeNetwork", "resetNetwork"]:
        print("[ error ] Unsupported command")
        exit()

    rpi_controller = RpiController()
    commander = getattr(rpi_controller, command)

    device = "eth0"
    ip = ""
    gateway = ""
    netmask = ""
    dns_prefer = ""
    dns_alter = ""

    if command == "changeNetwork" or command == "resetNetwork":
        try:
            device = sys.argv[2]
            ip = sys.argv[3]
            gateway = sys.argv[4]
            netmask = sys.argv[5]
            dns_prefer = sys.argv[6]
            dns_alter = sys.argv[7]
        except:
            pass       
    
    result = commander(device, ip, gateway, netmask, dns_prefer, dns_alter)    
    print("result:\n%s" % result)
