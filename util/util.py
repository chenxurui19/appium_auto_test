# -*- coding: utf-8 -*-
# @Time    : 2023/4/24 19:57
# @Author  : CXRui
# @File    : util.py
# @Description :
import socket
import random
import subprocess
import time
import requests
import os


def create_port(host, start, end):
    """
    创建空闲的端口号
    :param host: ip
    :param start:
    :param end:
    :return:
    """
    while True:
        num = random.randint(start, end)
        s = socket.socket()
        s.settimeout(0.5)
        try:
            if s.connect_ex((host, num)) != 0:
                return num
        finally:
            s.close()


def get_iphone_name(device_sn):
    """
    获取iphone手机的名字
    :param device_sn: 设备号
    :return:
    """
    name = None
    my_env = os.environ.copy()
    my_env["PATH"] = "/usr/local/bin:" + my_env["PATH"]
    p = subprocess.Popen("idevicename -u {}".format(device_sn), shell=True, stdout=subprocess.PIPE, env=my_env)
    p.wait()
    out, err = p.communicate()
    for line in out.splitlines():
        info = line.decode("utf-8")
        if info is not None and info != '':
            name = info
    if not name:
        from tidevice._device import Device
        t = Device(udid=device_sn)  # iOS设备
        name = t.name
    return name


def get_iphone_version(device_sn):
    """
    获取iphone的手机版本号
    :param device_sn: 设备号
    :return:
    """
    p = subprocess.Popen("ideviceinfo -u {} -k ProductVersion".format(device_sn),
                         shell=True, stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()
    for line in out.splitlines():
        info = line.decode("utf-8")
        if info and "ERROR" not in info:
            return info
        else:
            from tidevice._device import Device
            t = Device(udid=device_sn)  # iOS设备
            return t.get_value().get('ProductVersion')


def check_appium_port_available(port=4723):
    """
    检查appium服务是否启动起来
    :param port:
    :return:
    """
    url = "http://127.0.0.1:{}/wd/hub/status".format(port)
    proxies = {"http": None, "https": None}
    time.sleep(10)
    try:
        response = requests.get(url, proxies=proxies)
    except BaseException as e:
        response = None
        print(e)
    if response:
        if response.status_code == 200:
            return True
        else:
            return False
    else:
        return False