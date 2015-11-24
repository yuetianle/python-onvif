#!/usr/bin/env python
from onvif import ONVIFCamera
import onvif
import os
import sys
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
    #def get_stream_url(self, stream_urls=None):
    def get_stream_url(self, out_data=None):
        media_capability_name ='Meda'
        media_info = self.camera.devicemgmt.GetCapabilities({'Categroy':media_capability_name})
        if out_data is None:
            print("come here")
            out_data = list()


        #print(media_info)
        if media_info.Media.StreamingCapabilities.RTP_RTSP_TCP or media_info.Media.StreamingCapabilities.RTP_TCP:
            media_service = self.camera.create_media_service()
            profiles = media_service.GetProfiles()
            url_nodes = ET.Element('stream_url_lists')
            for item in profiles:
                #print(item._token)
                stream = {'StreamSetup':{'StreamType':'RTP_unicast','Transport':'RTSP'}, 'ProfileToken':item._token}
                stream_url = media_service.GetStreamUri(stream)
                #print(stream_url.Uri)
                url_node  = ET.SubElement(url_nodes,'stream_url')
                url_node.text = stream_url.Uri
            #url_tree = ET.ElementTree(url_nodes)
            #ET.dump(url_nodes)
            if type(out_data) == list:
                out_data.append(ET.tostring(url_nodes))
            elif type(out_data) == str:
                out_data.join(ET.tostring(url_nodes))
            print(out_data)

    def get_device_status(self, out_data, out_data_type):
        """get device current status"""
        return 0
    def add_user(self, out_data, username, password, level=None):
        """add a user to device"""
        if level is None:
            level = 'Operator'
        print(locals())
        user = {'User':{'Username':username, 'Password':password, 'UserLevel':level}}
        out_response = self.camera.devicemgmt.CreateUsers(user)
        print(out_response)
    def del_user(self, username):
        """ delete a device user."""
        user = {'Username':username}
        out_response = self.camera.devicemgmt.DeleteUsers(user)
        print(out_response)

def register_device(device_id, ip, port, username, password):
    print locals()
    if not device_list.has_key(device_id):
        client = onvif_host(ip, port, username, password)
        device_list[device_id] = client
    print(len(device_list))
def unregister_device(device_id):
    if device_list.has_key(device_id):
        del device_list[device_id]
def request_onvif_cmd(device_id, cmd, out_params = None, **in_params):
    print locals()
    if device_list.has_key(device_id):
        if cmd in dir(onvif_host) and hasattr(device_list[device_id], cmd):
            cmd_func = getattr(device_list[device_id], cmd)
            print(len(in_params))
            #print(out_params)
            if 0 < len(in_params):
                #in_param = in_params.items()
                in_param = in_params.values()
                print(in_param)
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
    #urls = list()
    #request_onvif_cmd(device_id,'get_stream_url', out_params = urls)
    #print(urls)

    '''
    test_host = onvif_host(ip, port, username, password)
    out_user_response = list()
    params = {'out_data':out_user_response, 'username':'onvif_test', 'password':'12345'}
    #test_host.add_user(out_user_response, username='onvif_test', password='12345')
    test_host.add_user(params)
    '''
    out_user_response = list()
    request_onvif_cmd(device_id,'add_user', out_params = out_user_response, username='onvif_test124', password='12345')
    raw_input()

