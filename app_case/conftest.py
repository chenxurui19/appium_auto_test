# -*- coding: utf-8 -*-
# @Time    : 2023/4/24 19:12
# @Author  : CXRui
# @File    : conftest.py
# @Description : pytest特有的测试配置文件，可以理解成一个专门放fixture(设备、工具)的地方
import logging
import os.path
import sys
import allure
import subprocess
import pytest
from datetime import datetime
from util import util
from config.config import GlobalVar
import time
import signal
from appium import webdriver
from urllib.parse import quote
from py.xml import html

src = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
server_ip = "127.0.0.1"  # appium服务运行的ip，一般appium服务和脚本都在同一台电脑上执行，使用'127.0.0.1'不需要修改
appium_port = 4723  # appium服务监听的端口，4723是初始值，执行过程中由脚本随机分配一个空闲端口，不需要人工介入
wda_port = 8100  # webdriveragent服务监听的端口，8100是初始值，执行过程中由脚本随机分配一个空闲端口，不需要人工介入
system_port = 8200  # adb转发端口，8200是初始值，执行过程中由脚本随机分配一个空闲端口，不需要人工介入
device_sn = ""  # 手机sn号，脚本从执行命令中读取后重新赋值
appium_p = None
driver = None
platform = ""  # 手机平台，android或ios
date_format = '%Y-%m-%d_%H.%M.%S'
rp_logger = None

"""
1、-session：顶层的fixture,该目录下所有的测试文件执行前会执行一次，只执行一次。
2、-module：模块级别的fixture，该目录下每个测试文件执行前都会执行一次。
3、-class：类级别的fixture，该目录下每个测试类执行前会执行一次
4、function：方法级别的fixture，每个方法执行前 都会执行一次。
"""


@pytest.fixture(scope="session")
def appium_setup(request):
    global device_sn, platform, appium_port, device_name, platform_version, wda_port, system_port, appium_port

    GlobalVar.set_device_sn(device_sn(request))
    GlobalVar.set_bundle_id(bundle_id(request))
    GlobalVar.set_app_activity(app_activity(request))

    appium_log_dir = f"{src}/appium_log/"  # appium_log文件夹，如不存在就创建
    if not os.path.exists(appium_log_dir):
        os.makedirs(appium_log_dir)

    pytest_log_dir = f"{src}/pytest_log/"
    if not os.path.exists(pytest_log_dir):
        os.makedirs(pytest_log_dir)

    report_dir = f"{src}/html_report/"  # html_report文件夹，如不存在就创建
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    appium_port = util.create_port(server_ip, 4723, 7999)  # 创建空闲的appium端口号
    appium_log_path = "{}{}_{}.log".format(appium_log_dir, datetime.now().strftime(date_format),
                                           appium_port)  # appium log存放的位置

    # 如果手机的设备号大于20，则为ios设备，否则为android
    if len(GlobalVar.get_device_sn()) > 20:
        platform = GlobalVar.IOS
        GlobalVar.set_test_platform(platform)
        wda_port = util.create_port(server_ip, 8100, 9999)  # 创建空闲的wda端口号
        device_name = util.get_iphone_name(GlobalVar.get_device_sn())
        platform_version = util.get_iphone_version(GlobalVar.get_device_sn())
        appium_p = subprocess.Popen(
            "appium -a {} -p {} --webdriveragent-port {} --relaxed-security "
            "--session-override --no-reset> {} 2>&1 &"
            .format(server_ip, appium_port, wda_port, appium_log_path), stdout=subprocess.PIPE,
            shell=True, preexec_fn=os.setsid)  # 命令行启动appium服务

        # 如果没起来 就会进死循环 一直换端口 起appium服务
        while not util.check_appium_port_available(appium_port):
            util.wait_appium_port_available(appium_port)
            if util.check_appium_port_available(appium_port):
                break
            appium_port = util.create_port(server_ip, 4723, 7999)
            appium_p = subprocess.Popen(
                "appium -a {} -p {} --webdriveragent-port {} --relaxed-security "
                "--session-override --no-reset> {} 2>&1 &"
                .format(server_ip, appium_port, wda_port, appium_log_path), stdout=subprocess.PIPE,
                shell=True, preexec_fn=os.setsid)  # 命令行启动appium服务
    else:
        platform = GlobalVar.ANDROID
        GlobalVar.set_test_platform(platform)
        system_port = util.create_port(server_ip, 8200, 8299)
        if sys.platform.startswith("win"):
            appium_p = subprocess.Popen(
                "appium -a {} -p {} --relaxed-security --session-override --no-reset> {} 2>&1 &"
                .format(server_ip, appium_port, appium_log_path), shell=True)  # 命令行启动appium服务
        else:
            appium_p = subprocess.Popen(
                "appium -a {} -p {} --relaxed-security --session-override --no-reset> {} 2>&1 &"
                .format(server_ip, appium_port, appium_log_path), stdout=subprocess.PIPE, shell=True,
                preexec_fn=os.setsid)  # 命令行启动appium服务
        time.sleep(10)

    import logging
    from pytest_reportportal import RPLogger, RPLogHandler
    global rp_logger
    rp_logger = logging.getLogger(__name__)
    rp_logger.setLevel(logging.DEBUG)
    # Create handler for Report Portal if the service has been
    # configured and started.
    if hasattr(request.node.config, 'py_test_service'):
        # Import Report Portal logger and handler to the test module.
        logging.setLoggerClass(RPLogger)
        rp_handler = RPLogHandler(request.node.config.py_test_service)
        # Add additional handlers if it is necessary
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        rp_logger.addHandler(console_handler)
    else:
        rp_handler = logging.StreamHandler(sys.stdout)
    # Set INFO level for Report Portal handler.
    rp_handler.setLevel(logging.INFO)
    GlobalVar.set_rp_logging(rp_logger)

    def kill_appium():
        try:
            if sys.platform.startswith("win"):
                p = os.popen("netstat -ano | findstr {}".format(appium_port))
                out = p.read().strip()
                begin = out.find("LISTENING") + len("LISTENING")
                end = out.find("\n", start=begin)
                pid = out[begin:end]
                os.popen("taskkill -PID {} -F".format(pid))
            else:
                os.killpg(os.getpgid(appium_p.pid + 1), signal.SIGTERM)  # 测试结束后，将appium进程杀掉
        except:
            pass
    # 注册kill_appium()为终结函数
    request.addfinalizer(kill_appium)


@pytest.fixture()
def driver_setup(request):
    """
    创建appium会话
    :param request:
    :return:
    """
    global driver, device_sn, device_name, platform_version, wda_port, platform
    if platform == GlobalVar.IOS:
        desired_capabilities = {
            "automationName": "XCUITest",
            "platformName": "ios",
            "deviceName": device_name,
            "bundleId": GlobalVar.get_bundle_id(),
            "udid": GlobalVar.get_device_sn(),
            "wdaLocalPort": wda_port,
            "newCommandTimeout": 3600,
            "clearSystemFiles": True,
            "wdaLaunchTimeout": 300000,
            "wdaConnectionTimeout": 300000,
            "noReset": True,
            "autoLaunch": False,
            "autoAcceptAlerts": False   # 自动关闭弹窗
        }
    else:
        desired_capabilities = {
            "automationName": "UiAutomator2",
            "platformName": "Android",
            "appPackage": GlobalVar.get_bundle_id(),
            "appActivity": GlobalVar.get_app_activity(),
            "udid": GlobalVar.get_device_sn(),
            "newCommandTimeout": 3600,
            "uiautomator2ServerInstallTimeout": 120000,
            "uiautomator2ServerLaunchTimeout": 120000,
            "systemPort": system_port,
            "orientation": "PORTRAIT",
            "noReset": True,
            "fullReset": False,
            "autoLaunch": False,
            "autoGrantPermissions": True
        }
    request.instance.driver = webdriver.Remote(command_executor='http://{}:{}/wd/hub'.format('127.0.0.1', appium_port),
                                               desired_capabilities=desired_capabilities)  # 创建会话
    request.instance.platform = platform
    driver = request.instance.driver
    if driver:
        logging.info(f"driver init finish...................")


def get_description(item):
    """
    获取用例函数的注释
    :param item: 
    :return: 
    """
    doc = str(item.function.__doc__)
    index = doc.find(":param")
    if index == -1:
        index = doc.find(":return:")
    if index != -1:
        return doc[:index]
    else:
        return doc
    
    
def make_path(node_id):
    """
    创建保存失败截图和日志的文件目录
    :param node_id:
    :return:
    """
    base_path = node_id.replace("()", "").replace("::::", "::").replace("::", "/")
    path = "{}/html_report/{}".format(src, base_path)
    html_path = "../html_report/{}".format(base_path)
    if not os.path.exists(path):
        os.makedirs(path)
    return path, html_path


def save_screenshot(path, html_path, name):
    """
    保存截图到html报告
    :param path:
    :param html_path:
    :param name:
    :return:
    """
    global driver
    path_name = '{}/{}.png'.format(path, name)
    html_path_name = '{}/{}.png'.format(html_path, name)
    print(f'driver instance>>>>>>>>>>>>>>>>>>: {driver}')
    driver.get_screenshot_as_file(path_name)
    html = '<div><img src="{}" alt="screenshot" width="180" height="320"' \
           'onclick="window.open(this.src)" align="right"/></div>'.format(html_path_name)
    return html


def save_appium_log(path, html_path, name):
    """
    获取appium server的缓存日志，并保存到报告中
    :param path:
    :param html_path:
    :param name:
    :return:
    """
    appium_server_path = '{}/appium_sever_{}.log'.format(path, name)
    html_path_name = '{}/appium_sever_{}.log'.format(html_path, name)
    log = driver.get_log('server')
    f = open(appium_server_path, "w+", encoding="utf-8")
    for line in log:
        f.write(line['message'] + '\n')
    f.close()
    appium_url = quote(html_path_name)
    html = '<div><a href="{0}">{0}</a></div>'.format(appium_url)
    return html


def save_device_log(path, html_path, name):
    """
    获取测试机的缓存日志，并保存
    :param path: 
    :param html_path: 
    :param name: 
    :return: 
    """
    global platform
    logs = []
    logcat_path = '{}/logcat_{}.log'.format(path, name)
    html_path_name = '{}/logcat_{}.log'.format(html_path, name)
    if platform == GlobalVar.IOS:
        logs = driver.get_log('syslog')
    else:
        for _ in range(3):
            log = driver.get_log('logcat')
            logs.extend(log)
            # time.sleep(60)
    f = open(logcat_path, "w+", encoding="utf-8")
    for line in logs:
        f.write(line['message'] + '\n')
    f.close()
    logcat_url = quote(html_path_name)
    html = '<div><a href="{0}">{0}</a></div>'.format(logcat_url)
    return html


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    """
    Extends the PyTest Plugin to take and embed screenshot in html report, whenever test fails.
    :param item:
    """
    global driver, date_format
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    report.description = get_description(item)
    report.nodeid = report.nodeid.encode("utf-8").decode("unicode_escape")
    extra = getattr(report, 'extra', [])

    if report.when == 'call' or report.when == "setup":  # or report.when == "teardown"
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            path, html_path = make_path(report.nodeid)
            name = datetime.now().strftime(date_format)
            screenshot_html = save_screenshot(path, html_path, name)
            extra.append(pytest_html.extras.html(screenshot_html))
            appium_log_html = save_appium_log(path, html_path, name)
            extra.append(pytest_html.extras.html(appium_log_html))
            device_log_html = save_device_log(path, html_path, name)
            extra.append(pytest_html.extras.html(device_log_html))
            report.extra = extra

            global logcat_name
            logcat_name = '{}/logcat_{}.log'.format(path, name)
            mode = "a" if os.path.exists("failures") else "w"
            with open("failures", mode) as f:
                # let's also access a fixture for the fun of it
                if "tmpdir" in item.fixturenames:
                    extra = " (%s)" % item.funcargs["tmpdir"]
                else:
                    extra = ""
                f.write(report.nodeid + extra + "\n")
                # global driver
                path = allure_path()
                name = datetime.now().strftime('%m%d%H%M%S')
                path_name = u'{}/{}.png'.format(path, name)
                driver.get_screenshot_as_file(path_name)
                allure.attach.file(path_name, "【断言失败截图:{}.png】".format(name), allure.attachment_type.PNG)

                with open('{}/{}.png'.format(path, name), "rb") as image_file:
                    GlobalVar.get_rp_logging().info("failure screenshot",
                                                    extra=dict(attachment={"name": "failure screenshot.png",
                                                                           "data": image_file,
                                                                           "mime": "image/png"}))
                #  这里写添加日志
                path = allure_path()
                name = datetime.now().strftime('%m%d%H%M%S')
                path_name = u'{}.log'.format(name)
                allure.attach.file(logcat_name, "【断言失败日志:{}】".format(path_name), allure.attachment_type.TEXT)

                with open(logcat_name, "rb") as log_file:
                    GlobalVar.get_rp_logging().info("failure logcat",
                                                    extra=dict(attachment={"name": "failurelogcat.txt",
                                                                           "data": log_file,
                                                                           "mime": "text/plain"}))


def allure_path():
    """
    allure报告目录
    :return:
    """
    global src
    path = src.replace("/src", "")
    path1 = '{}/allure-report'.format(path)
    if not os.path.exists(path1):
        os.makedirs(path1)
    path2 = '{}/allure-results'.format(path)
    if not os.path.exists(path2):
        os.makedirs(path2)
    path3 = '{}/result_images'.format(path)
    if not os.path.exists(path3):
        os.makedirs(path3)
    return path3


def pytest_configure(config):
    """
    在pytest-html报告Environment项中添加自定义内容，配置报告路径
    :param config:
    :return:
    """
    time_string = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    config.option.htmlpath = "{}/html_report/report_{}.html".format(src, time_string)  # 配置报告路径和报告名


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    """
    pytest-html报告中新增'Description','Test_nodeid'列
    :param cells:
    :return:
    """
    cells.insert(1, html.th('Description'))
    cells.insert(2, html.th('Test_nodeid'))
    cells.pop(2)


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    """
    报告中新增的'Description'列内容显示每条case的注释，如果没有写注释则为空，不显示
    'Test_nodeid'列内容显示每条case的名字
    :param report:
    :param cells:
    :return:
    """
    try:
        cells.insert(1, html.td(report.description))
        cells.insert(2, html.td(report.nodeid))
        cells.pop(2)
    except:
        pass


def pytest_addoption(parser):
    """
    注册参数
    :param parser:
    :return:
    """
    parser.addoption("--device_sn", action="store", default="", help="手机设备号")
    parser.addoption("--bundle_id", action="store", default="com.android.settings", help="包名")
    parser.addoption("--app_activity", action="store", default="com.android.settings.Settings", help="启动activity")


def device_sn(request):
    """
    脚本获取命令行参数的接口：获取手机设备号
    :param request:
    :return:
    """
    value = request.config.getoption("--device_sn")
    return value


def bundle_id(request):
    """
    脚本获取命令行参数的接口：获取包名
    :param request:
    :return:
    """
    value = request.config.getoption("--bundle_id")
    return value


def app_activity(request):
    """
    脚本获取命令行参数的接口：获取启动activty
    :param request:
    :return:
    """
    value = request.config.getoption("--app_activity")
    return value
