'''
Created on 7 Mar 2018

@author: gavin
'''
from lib.core import errors
from lib.core.log import CustomLogger
from lib.core import settings

import threading
import time
import requests
import os
import base64
import logging

logging.setLoggerClass(CustomLogger)
LOG = logging.getLogger(settings.APPLICATION)

class CatcherClient(object):
    '''
    Used for communicating with the callbackcatcher server
    '''
    BASE_REST_PATH = 'api/'
    PORT_PATH = os.path.join(BASE_REST_PATH, 'port/')
    CALLBACK_PATH = os.path.join(BASE_REST_PATH, 'callback/')
    STATUS_PATH = os.path.join(BASE_REST_PATH, 'status/')
    SECRET_PATH = os.path.join(BASE_REST_PATH, 'secrets/')
    REQUEST_PATH = os.path.join(BASE_REST_PATH, 'request/')
    HANDLER_PATH = os.path.join(BASE_REST_PATH, 'handler/')

    def __init__(self, ipaddress, port, user, password):
        """
        Constructor
        """
        self.ipaddress = ipaddress
        self.port = port
        self.username = user
        self.password = password
        self.url = "http://{0}:{1}/".format(self.ipaddress, self.port)
        
    def _send_post(self, path, data):
        """
        Sends a simple post request to the rest endpoint
        
        :param      path: location of endpoint
        :param      data: dict of data
        :return:    return response or None
        """
        resp = None
        url = "%s%s" % (self.url, path)
        resp = requests.post(url,
                          verify=False,
                          auth=(self.username, self.password),
                          json=data)
        return resp
        
    def _send_get(self, path):
        """
        Sends a simple get request to the rest endpoint
        
        :param      path: location of endpoint
        :return:    return response or None
        """
        resp = None
        url = "%s%s" % (self.url, path)
        resp = requests.get(url,
                          verify=False,
                          auth=(self.username, self.password))
        if resp.status_code != 200:
            raise ValueError("Error")
        return resp
    
    def _get_handlers(self):
        resp = self._send_get(self.HANDLER_PATH)
        return resp.json()
            
    def check_connection(self):
        """
        Connect to catcher endpoint
        
        :return:    True if endpoint is alive
        """
        try:
            resp = self._send_get(self.STATUS_PATH)
            if resp.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            return False
        except Exception as e:
            LOG.error(e)
        else:
            return False
    
    def get_status(self):
        """
        Connect to catcher endpoint, login and get status
        
        :return:    True if endpoint is alive
        """
        response = self._send_get(self.STATUS_PATH)
        return response.json()
    
    def get_callbacks(self):
        """
        Get all callbacks
        
        :return:    dict object
        """
        response = self._send_get(self.CALLBACK_PATH)
        return response.json()
    
    def get_ports(self):
        """
        Get all ports
        
        :return:    dict object
        """
        response = self._send_get(self.PORT_PATH)
        return response.json()
    
    def get_callback_by_source(self, ip=None, port=None):
        """
        Get all callbacks by a given source ip
        
        :return:    dict object
        """
        r = []
        if ip != None and port != None:
            for cb in self.get_callbacks():
                if cb['sourceip'] == ip and cb['serverport'] == port:
                    r.append(cb)
        elif ip != None and port == None:
            for cb in self.get_callbacks():
                if cb['sourceip'] == ip:
                    r.append(cb)
        elif ip == None and port != None:
            for cb in self.get_callbacks():
                if cb['serverport'] == port:
                    r.append(cb)
        return r
    
    def register_token(self, token):
        """
        Add a unique string to search for in each callback
        
        :param      unique string
        """
        data = {}
        resp = self._send_post(self.REQUEST_PATH, data)
        print(resp)
        
    def start_port(self, port, protocol='tcp', handler=None, ssl=False):
        """
        Tell callbackcatcher server to start a service
        
        :param      port number to start
        :return:    single dictionary item of give id
        """
        if ssl is False:
            ssl = 0
        else:
            ssl = 1
        
        handlerid = None
        for h in self._get_handlers():
            if handler in h['filename']:
                handlerid = h['id']
                break
        data = {"number":port, "protocol":protocol, "handler":handlerid, "ssl":ssl}
        resp = self._send_post(self.PORT_PATH, data)
        print(resp)
        
    def stop_port(self, port, protocol='tcp'):
        """
        Tell callbackcatcher server to stop a service
        
        :param      port number to start
        :return:    single dictionary item of give id
        """
        resp = None
        ports = self.get_ports()
        for p in ports:
            if p['number'] == port and p['protocol'] == protocol:
                pid = resp.json()['pid']
                resp = self._send_post({'pid': pid})
                return True
        return False
    
    def get_response(self, id):
        """
        Get list of callbacks found for a given request id
        
        :param      id: hash value of the request
        :return:    single dictionary item of given id
        """
        response = self._send_get(self.REQUEST_PATH)
        for i in response:
            print(i)
        return response.json()
    
    
class CatcherPoll(threading.Thread):
    """
    Used for background polling
    """
    def __init__(self, catcher, poll):
        self.catcher = catcher
        self.poll = poll
        threading.Thread.__init__(self)

    def run(self):
        time.sleep(self.poll)
        
if __name__ == '__main__':
    import sys
    from lib.core.request import RawRequest
    raw = """GET / HTTP/1.1
Host: GAV-PC
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-GB,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: https://www.pentestlabs.co.uk/login
Cookie: GEAR=local-5a1d8985bc517715b7000234
Connection: Close
Upgrade-Insecure-Requests: 1

test=1&test2=2

test=1&test2=2

test=1&test2=2

"""
    req = RawRequest('127.0.0.1', 9999, raw, is_ssl=False)
    print("start")
    client = CatcherClient('127.0.0.1', 12444, '', '')
    try:
        if client.check_connection() is False:
            print("CallbackCatcher server is not online :(")
            sys.exit()
        print(client.get_status())
        print(client.get_callbacks())
        print(client.get_callback_by_source(port=88))

        client.start_port(53, 'udp', handler='dns', ssl=False)
        client.start_port(80, 'tcp', handler='static_http', ssl=False)
        client.start_port(443, 'tcp', handler='static_http', ssl=True)

    except errors.CatcherClientConnectionError:
        print("Failed to connect to server")
    print("finish")