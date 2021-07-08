'''
Created on 5 Mar 2018

@author: gavin
'''
from lib.core import settings
from lib.core.log import CustomLogger
from lib.core.request import RawRequest
from lib.core.enums import INJECT_MATCH_REPLACE
from lib.core.enums import INJECT_HEADERS

import logging
import re
import copy

logging.setLoggerClass(CustomLogger)
LOG = logging.getLogger(settings.APPLICATION)

def ip_match_replace(request, injectionstring):
    """
    Simple match and replace of string within request
    """
    newrequest = copy.deepcopy(request)
    rawrequest = request.get_raw_request()
    for r in INJECT_MATCH_REPLACE:
        regex = re.compile(r)
        if regex.search(rawrequest):
            LOG.tamper("IP detected! Replaced with {}".format(injectionstring))
            newrawreq = re.sub(regex, injectionstring, rawrequest)
            newrequest.set_raw_request(newrawreq)
    return newrequest

def inject_headers(request, injectionstring):
    """
    Generates a list of new requests with modified headers
    
    :param    request:             request instance
    :param    injection_string:    list of strings to inject into the request
    :return:  list of requests
    """
    newrequest = copy.deepcopy(request)
    print(injectionstring)
    for header in INJECT_HEADERS:
        headername, headervalue = header.split(":", 1)
        if not request.get_header(headername):
            LOG.debug("Added {} header to the request".format(header))
            newrequest.add_header(headername,headervalue)
        else:
            LOG.debug("Request already has a header with that name")
        
    return newrequest

def inject_post_param(request, injectionstring):
    """
    Generates a list of new requests with replaced/modified post parameters
    
    :param    request:             request instance
    :param    injection_string:    list of strings to inject into the request
    :return:  list of requests
    """
    requests = []
    return requests

def inject_get_param(request, injectionstring):
    """
    Generates a list of new requests with replaced/modified POST values
    
    :param    request:             request instance
    :param    injection_string:    list of strings to inject into the request
    :return:  list of requests
    """
    requests = []
    return requests
    
def inject_pipeline(request, injectionstring):
    """
    Generates a list of new pipelined requests
    
    :param    request:             request instance
    :param    injection_string:    list of strings to inject into the request
    :return:  list of requests
    """
    requests = []
    
    
    
    return requests