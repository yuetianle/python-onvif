#!/usr/bin/env python
#coding=utf8
from onvif import ONVIFCamera
import onvif
import os
import types
import sys
import inspect

import logging

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

try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET
device_list = dict()
func_lists =['get_stream_url', 'add_user', 'del_user', 'alter_user']
class onvif_host:
    '''
    onvif device class info
    '''
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        if sys.platform == 'win32':
            wsdl_path = os.path.join(os.path.dirname(onvif.__file__), os.path.pardir, "wsdl")
            self.camera = ONVIFCamera(ip, port, username, password, wsdl_path)
        else:
            self.camera = ONVIFCamera(ip, port, username, password)

    def __check_user_exist__(self, username, users = None):
        user_lists = self.camera.devicemgmt.GetUsers()
        if users is None:
            users = dict()
        users.clear()
        user_name_lists = list()
        for user_item in user_lists:
            user_name_lists.append(user_item.Username)
            if not users.has_key(user_item.Username) and user_item.Username == username:
                if hasattr(user_item, 'Username'):
                    users['Username'] = user_item.Username
                if hasattr(user_item, 'Password'):
                    users['Password'] = user_item.Password
                if hasattr(user_item, 'UserLevel'):
                    users['UserLevel'] = user_item.UserLevel
        if username not in user_name_lists:
            return False
        else:
            return True

    def get_stream_url(self, out_data=None):
        media_capability_name ='Meda'
        media_info = self.camera.devicemgmt.GetCapabilities({'Categroy':media_capability_name})
        if out_data is None:
            out_data = list()

        if media_info.Media.StreamingCapabilities.RTP_RTSP_TCP or media_info.Media.StreamingCapabilities.RTP_TCP:
            media_service = self.camera.create_media_service()
            profiles = media_service.GetProfiles()
            url_nodes = ET.Element('stream_url_lists')
            for item in profiles:
                stream = {'StreamSetup':{'StreamType':'RTP_unicast','Transport':'RTSP'}, 'ProfileToken':item._token}
                stream_url = media_service.GetStreamUri(stream)
                url_node  = ET.SubElement(url_nodes,'stream_url')
                url_node.text = stream_url.Uri
            if type(out_data) == list:
                out_data.append(ET.tostring(url_nodes))
            elif type(out_data) == str:
                out_data.join(ET.tostring(url_nodes))
    def get_device_status(self, out_data, out_data_type):
        """get device current status"""
        return 0
    def add_user(self, out_data, username, password, level=None):
        """add a user to device"""
        logger.debug(locals())
        if level is None:
            level = 'Operator'
        user = {'User':{'Username':username, 'Password':password, 'UserLevel':level}}
        user_lists_node = ET.Element('user_lists')
        user_content    = ET.SubElement(user_lists_node, 'user')
        user_content.set('name', username)
        if self.__check_user_exist__(username):
            user_content.text = 'False'
            user_content.set('error_message', 'user exist')
        else:
            try:
                out_response = self.camera.devicemgmt.CreateUsers(user)
                user_content.text = 'True'
            except:
                user_content.text = 'False'
        out_data.append(ET.tostring(user_lists_node))
    def del_user(self, out_data, username):
        """ delete a device user."""
        logger.debug(locals())
        user = {'Username':username}
        user_lists_node = ET.Element('user_lists')
        user_content    = ET.SubElement(user_lists_node, 'user')
        user_content.set('name', username)
        if self.__check_user_exist__(username):
            out_response = self.camera.devicemgmt.DeleteUsers(user)
            user_content.text = 'True'
        else:
            user_content.text = 'False'
            user_content.set('error_message', 'user not exist')
        if type(out_data) == types.ListType:
            out_data.append(ET.tostring(user_lists_node))

    def alter_user(self, out_data, username, level, password=None):
        """alter device user info"""
        logger.debug(locals())
        users = dict()
        user_lists_node = ET.Element('user_lists')
        user_content    = ET.SubElement(user_lists_node, 'user')
        user_content.set('name', username)
        if self.__check_user_exist__(username, users):
            if password is None:
                user = {'User':{'Username':username, 'UserLevel':level}}
                self.camera.devicemgmt.SetUser(user)
            else:
                user = {'User':{'Username':username, 'UserLevel':level, 'Password':password}}
                self.camera.devicemgmt.SetUser(user)
            user_content.text = 'True'
        else:
            logger.warning("user %s not exitst", username)
            user_content.text = 'False'
        out_data.append(ET.tostring(user_lists_node))


def register_device(device_id, ip, port, username, password):
    logger.debug(locals())
    if not device_list.has_key(device_id):
        client = onvif_host(ip, port, username, password)
        device_list[device_id] = client
def unregister_device(device_id):
    if device_list.has_key(device_id):
        del device_list[device_id]
def request_onvif_cmd(device_id, cmd, out_params = None, **in_params):
    logger.debug(locals())
    if device_list.has_key(device_id):
        if cmd in dir(onvif_host) and hasattr(device_list[device_id], cmd):
            cmd_func = getattr(device_list[device_id], cmd)
            params_lists = []
            for call_args in inspect.getargspec(cmd_func).args:
                if in_params.has_key(call_args):
                    params_lists.append(in_params.get(call_args))
            logger.debug("cmd=%s args:%s args_value:%s", cmd, inspect.getargspec(cmd_func).args, params_lists)
            if 0 < len(in_params):
                in_param = params_lists
                if out_params is not None:
                    if 1 == len(in_param):
                        cmd_func(out_params, in_param[0])
                    elif 2 == len(in_param):
                        cmd_func(out_params, in_param[0], in_param[1])
                    elif 3 == len(in_param):
                        cmd_func(out_params, in_param[0], in_param[1], in_param[2])
                    elif 4 == len(in_param):
                        cmd_func(out_params, in_param[0], in_param[1], in_param[2], in_param[3])
                    elif 5 == len(in_param):
                        cmd_func(out_params, in_param[0], in_param[1], in_param[2], in_param[3], in_param[4])
                else:
                    if 1 == len(in_param):
                        cmd_func(in_params[0])
                    elif 2 == len(in_param):
                        cmd_func(in_param[0], in_param[1])
                    elif 3 == len(in_param):
                        cmd_func(in_param[0], in_param[1], in_param[2])
                    elif 4 == len(in_param):
                        cmd_func(in_param[0], in_param[1], in_param[2], in_param[3])
                    elif 5 == len(in_param):
                        cmd_func(in_param[0], in_param[1], in_param[2], in_param[3], in_param[4])
            else:
                if out_params is not None:
                    cmd_func(out_params)
                elif out_params is None:
                    cmd_func()

if __name__ == '__main__':
    device_id = '172.16.1.221'
    ip = '172.16.1.221'
    port = 80
    username = 'admin'
    password = '12345'
    register_device(device_id, ip, port, username, password)
    urls = list()
    request_onvif_cmd(device_id,'get_stream_url', out_params = urls)

    '''
    test_host = onvif_host(ip, port, username, password)
    out_user_response = list()
    params = {'out_data':out_user_response, 'username':'onvif_test', 'password':'12345'}
    #test_host.add_user(out_user_response, username='onvif_test', password='12345')
    test_host.add_user(params)
    '''
    out_user_response = list()
    request_onvif_cmd(device_id,'add_user', out_params = out_user_response, username='onvif_test124', password='12345')
    out_user_response = list()
    #request_onvif_cmd(device_id,'del_user', out_params = out_user_response, username='onvif_test124')
    out_user_response = list()
    request_onvif_cmd(device_id,'alter_user', out_params = out_user_response, username='onvif_test124', level = 'User', password = 'OnvifTest123')
    #request_onvif_cmd(device_id,'alter_user', out_params = out_user_response, username='onvif_test124', level = 'User')
    raw_input()

