# -*- coding: utf-8 -*-
# @Time    : 2023/4/24 19:37
# @Author  : CXRui
# @File    : config.py
# @Description :

class GlobalVar:
    IOS = "ios"
    ANDROID = "android"
    DEVICE_SN = ""
    BUNDLE_ID = "com.android.settings"
    APP_ACTIVITY = "com.android.settings.Settings"
    TEST_PLATFORM = "ios"
    _RP_LOGGING = None

    @staticmethod
    def set_bundle_id(bundle_id):
        GlobalVar.BUNDLE_ID = bundle_id

    @staticmethod
    def get_bundle_id():
        return GlobalVar.BUNDLE_ID

    @staticmethod
    def set_app_activity(app_activity):
        GlobalVar.APP_ACTIVITY = app_activity

    @staticmethod
    def get_app_activity():
        return GlobalVar.APP_ACTIVITY

    @staticmethod
    def set_device_sn(device_sn):
        GlobalVar.DEVICE_SN = device_sn

    @staticmethod
    def get_device_sn():
        return GlobalVar.DEVICE_SN

    @staticmethod
    def set_test_platform(test_platform):
        GlobalVar.TEST_PLATFORM = test_platform

    @staticmethod
    def get_test_platform():
        return GlobalVar.TEST_PLATFORM

    @staticmethod
    def get_rp_logging():
        return GlobalVar._RP_LOGGING

    @staticmethod
    def set_rp_logging(rp_logging):
        GlobalVar._RP_LOGGING = rp_logging


