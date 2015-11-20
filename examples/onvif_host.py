#!/usr/bin/env python
from onvif import ONVIFCamera
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
        self.camera = ONVIFCamera(ip, port, username, password)
    def get_stream_url(self, stream_urls=None):
        media_capability_name ='Meda'
        media_info = self.camera.devicemgmt.GetCapabilities({'Categroy':media_capability_name})
        if stream_urls is None:
            stream_urls = []
        #print(media_info)
        if media_info.Media.StreamingCapabilities.RTP_RTSP_TCP or media_info.Media.StreamingCapabilities.RTP_TCP:
            media_service = self.camera.create_media_service()
            profiles = media_service.GetProfiles()
            for item in profiles:
                #print(item._token)
                stream = {'StreamSetup':{'StreamType':'RTP_unicast','Transport':'RTSP'}, 'ProfileToken':item._token}
                stream_url = media_service.GetStreamUri(stream)
                stream_urls.append(stream_url)
            #print(stream_urls)


def register_device(device_id, ip, port, username, password):
    client = onvif_host(ip, port, username, password)
    device_list[device_id] = client
def unregister_device(device_id):
    if device_list.has_key(device_id):
        del device_list[device_id]
def request_onvif_cmd(device_id, cmd, out_params = None, **in_params):
    if device_list.has_key(device_id):
        if cmd in dir(onvif_host):
            cmd_func = getattr(device_list[device_id], cmd)
            if 0 < len(in_params):
                in_param = in_params.items()

                if out_params is not None:
                    cmd_func(in_params, out_params)
                else:
                    cmd_func(in_param)
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
    urls = []
    request_onvif_cmd(device_id,'get_stream_url', out_params = urls)
    print(urls)
