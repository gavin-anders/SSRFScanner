'''
Created on 25 Feb 2018

@author: gavin
'''
from lib.core import settings
import datetime
import socket

def time_diff(oldtimestamp, newtimestamp=None):
    """
    returns difference in microseconds
    """
    delta = datetime.datetime.now() - oldtimestamp
    if newtimestamp:
        delta = newtimestamp - oldtimestamp
    return int(delta.microseconds)

def check_request_time(request, expcode=200):
    '''
    Check the request
    
    :param expcode: expected http status code
    :return: avg response time
    '''
    avgtime = 0
    times = []
    try:
        for i in range(settings.NUM_CHECKS):
            a = datetime.datetime.now()
            resp = request.send_request()
            if resp.status == expcode:
                b = datetime.datetime.now()
                delta = b - a
                times.append(int(delta.microseconds))
        if sum(times) != 0:
            avgtime = int(sum(times) / len(times))
    except Exception as e:
        print(e)
    return avgtime

def validate_port(port):
    if port > 0 and port < 65536:
        return True
    return False
        
def validate_ip(ip):
    try:
        socket.inet_aton(ip)
    except:
        return False
    return True

def validate_proxy(proxystr):
    try:
        proxyip, proxyport = proxystr.split(':')
        proxyport = int(proxyport)
    except:
        raise Exception("Invalid proxy string")
    
    if validate_ip(proxyip) is False:
        raise Exception("Invalid proxy IP address")
    if validate_port(proxyport) is False:
        raise Exception("Invalid proxy port")
    if validate_connectivity(proxyip, proxyport) is False:
        raise Exception("Unable to connect to proxy")
    
def validate_connectivity(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip,port))
    if result == 0:
        return True
    else:
        return False
