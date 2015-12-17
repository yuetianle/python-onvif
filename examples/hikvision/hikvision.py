#!/usr/bin/env python
# -*- coding: utf-8 -*-
import device_plugins_hikvision
import logging
from urlobject import URLObject

# 使用一个名字为fib的logger
logger = logging.getLogger('onvif_host')

# 设置logger的level为DEBUG
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.WARN)

# 创建一个输出日志到控制台的StreamHandler
hdr = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(funcName)s:%(lineno)s] : %(message)s')
hdr.setFormatter(formatter)
# 给logger添加上handler
logger.addHandler(hdr)

class hikvision_host(object):
    """hikvision host"""
    def __init__(self, uri, params, device_id):
        """ init function """
        self.uri = uri
        self.params = params
        self.device_id = device_id

class uri_parser():
    """uri parser"""
    def __init__(self, uri):
        """init function"""
        self.uri = URLObject(uri)
    def user_name(self):
        return self.uri.username
    def password(self):
        return self.uri.password
    def ip(self):
        return self.uri.hostname
    def port(self):
        return self.uri.port
    def func_name(self, name):
        query = self.uri.query.dict
        if query.has_key(name):
            return query[name]
        else:
            return ''
    def func_params(self, name):
        query = self.uri.query.dict
        query.pop(name)
        return query

def request_hikvision_cmd(device_id, uri, params, out_params, out_params_len):
    """device cmd"""
    func_lists = dir(device_plugins_hikvision)
    print(func_lists)
if __name__ == '__main__':
    test_parser = uri_parser("http://172.16.1.221:8000@admin:12345/device/meida?func=register_device&user=admin&password=12345&manufacturer_type=5&protocol_type=0&device_type=0")
    print(test_parser.user_name())
    print(test_parser.func_name())
    print(test_parser.func_params())
