'''
Created on 2 Mar 2018

@author: gavin
'''
from lib.core import settings
from lib.core.client import CatcherClient
from lib.core.request import RawRequest, RawResponse
from lib.core.log import CustomLogger
from lib.core.validators import check_request_time
from lib.core.validators import validate_port
from lib.core.validators import time_diff
from lib.core.utils import update
from lib.core.utils import stop_running
from lib.core.enums import BASE_URI_SCHEMES, EXTRA_URI_SCHEMES
from lib.core.enums import BASE_HOSTS, EXTRA_HOSTS
from lib.core.enums import BASE_POSTS

from lib.core import errors

from lib.core.inject import inject_get_param
from lib.core.inject import inject_post_param
from lib.core.inject import inject_headers
from lib.core.inject import inject_pipeline
from lib.core.inject import ip_match_replace

from lib.core.detect import detect_code_difference
from lib.core.detect import detect_content_difference
from lib.core.detect import detect_time_difference
from lib.core.detect import detect_error_messages

import logging
import sys
import datetime
import re
import time
import socket
import os

logging.setLoggerClass(CustomLogger)
LOG = logging.getLogger(settings.APPLICATION)

def init_request(ip, port, requestfile, proxy, ssl):
    '''
    Initialise and validate request
    
    :param filepath: path of request file
    :return: instance of raw request
    '''
    LOG.info("Initialising request")
    try:
        # parse proxy
        if proxy:
            proxyip, proxyport = proxy.split(":")
            proxy = (proxyip, int(proxyport))
        
        raw = requestfile.read()      
        request = RawRequest(ip, port, raw, is_ssl=ssl, proxy=proxy)
        response = request.send_request()
        response.read_response()
        
        if request.validate() is True:
            LOG.debug("Validated requested")
        
        # check we can access
        LOG.info("Testing if web server {}:{} is online...".format(ip, port))
        times = []
        resp_time = 0
        for i in range(settings.NUM_CHECKS):
            a = datetime.datetime.now()
            resp = request.send_request()
            if resp.status:
                b = datetime.datetime.now()
                delta = b - a
                times.append(int(delta.microseconds))
        if sum(times) != 0:
            resp_time = int(sum(times) / len(times))
    
        if resp_time == 0:
            LOG.exception("Unable to reach target webserver")
        else:
            LOG.debug("Average response time from server - %s microseconds" % resp_time)
            response.time = resp_time
        LOG.info("Web server seems to be online. Got good responses!")
        return request, response
    except ConnectionRefusedError:
        LOG.exception("Connection refused")
    except Exception as e:
        if "timed out" in str(e):
            LOG.exception("Connection timed out. Try increasing the timeout in settings.py")
        else:
            LOG.error(e)

def generate_ip_strings(iplist):
    # generate IP addresses
    iplist = BASE_HOSTS + iplist
    iplist.append('local.{}'.format(settings.CATCHER_DOMAIN))    
    iplist = list(set(iplist))
    tmpip = []
    for ip in iplist:
        tmpip.append("{}".format(ip))
    iplist = iplist + tmpip
    iplist = list(set(iplist))
    return iplist

def generate_injection_strings(hosts):
    ports = BASE_POSTS
    injectionstrings = []
    for uritemplate in BASE_URI_SCHEMES:
        for h in hosts:
            for p in ports:
                p = ':{}'.format(p)
                uri = uritemplate.format(host=h, port=p, ssl='')
                injectionstrings.append(uri)
                uri = uritemplate.format(host=h, port=p, ssl='s')
                injectionstrings.append(uri)
    injectionstrings = injectionstrings + hosts
    return list(set(injectionstrings))

def detect(request, base, iplist, args, client=None):    
    try:
        response = request.send_request()
        response.read_response()
        requestid = request.checksum

        # check for change in response codes
        if args.RESPCODE is True:
            if detect_code_difference(base, response) is True:
                LOG.info("{}: Response code differed".format(requestid))
                errors = detect_error_messages(response)
                if len(errors) > 0:
                    errmessage = detect_error_messages(response)
                    if errmessage:
                        LOG.info("{}: Detected error message in the response".format(requestid))
                        LOG.info("Error name: {}".format(errmessage["name"]))
                        LOG.info("Error type: {}".format(errmessage["type"]))
                        LOG.info("Error search: {}".format(errmessage["search"]))
        # check change in response size
        if args.CONTENT is True:
            if detect_content_difference(base, response) is True and args.CONTENT is True:
                LOG.info("{}: Response sizes differ".format(requestid))
        
        # check for change in response times
        if args.TIME is True:
            if detect_time_difference(base, response) is True and args.TIME is True:
                LOG.info("{}: Response times differ".format(requestid))

        # check for error messages
        if args.ERROR is True:
            errmessage = detect_error_messages(response)
            if errmessage:
                LOG.info("{}: Detected error message in the response".format(requestid))
                LOG.info("Error name: {}".format(errmessage["name"]))
                LOG.info("Error type: {}".format(errmessage["type"]))
                LOG.info("Error search: {}".format(errmessage["search"]))
        
    except Exception as e:
        LOG.error(e)
        raise

def main(ipaddress, port, args):
    # unpack variables
    param = args.PARAMETER
    enablessl = args.SSL

    if args.UPDATE is True:
        update()
        sys.exit()

    # set up some defaults
    if args.TIME is False and args.ERROR is False and args.RESPCODE is False and args.CONTENT is False:
        LOG.info("Looks like you didnt specify a detection method. Trying to detect everything!")
        args.ERROR = True
        args.RESPCODE = True
        args.TIME = True
        args.CONTENT = True
        
    LOG.info("Target: {}:{}".format(ipaddress, port))
    
    # form the request object
    baserequest, origresponse = init_request(ipaddress, port, args.REQUESTFILE, args.PROXY, args.SSL)
    
    # generate list of ip addresses strings
    hostheader = baserequest.get_header('Host')
    if ":" in hostheader:
        host, port = baserequest.get_header('Host').split(":", 1)
        iplist = generate_ip_strings([host])
    else:
        iplist = generate_ip_strings([])
        
    # make unique 
    iplist = list(set(iplist))
    
    # match and replace manipulation
    LOG.info("Attempting to match and replace existing IP addresses in original request")
    for ipstring in iplist:
        request = ip_match_replace(baserequest, ipstring)
        if request.checksum != baserequest.checksum:
            detect(request, origresponse, iplist, args)
            
    # generate injectable strings
    injectablestrings = generate_injection_strings(iplist)
    LOG.info("Generated {} unique injection strings".format(len(injectablestrings)))

    # header manipulation
    LOG.info("Attempting to inject headers")
    for ipstring in injectablestrings:
        request = inject_headers(baserequest, ipstring)
        if request.checksum != baserequest.checksum:
            detect(request, origresponse, iplist, args)
    
    # try oob attack
    #if args.OOB is True:
    ## check catcher client for callback name
    #client = CatcherClient(settings.CATCHER_IP, settings.CATCHER_PORT, settings.CATCHER_USER, settings.CATCHER_PASS)
    #try:
    #    if client.check_connection() is True:
    #        status = client.get_status()
    #        cblocalip = "local.{}".format(status['domain'])
    #        iplist.append(cblocalip)
    #        LOG.debug("Added {} to the IP list".format(cblocalip))
    #        cbexternalip = "catcher.{}".format(status['domain'])
    #        iplist.append(cbexternalip)
    #        LOG.debug("Added {} to the IP list".format(cbexternalip))
    #        cbclientip = "{}".format(status['clientip'])
    #        iplist.append(cbclientip)
    #        LOG.debug("Added {} to the IP list".format(cbclientip))
    #        iplist.append(settings.CATCHER_IP)
    #   else:
    #        LOG.warning("Callback client not responding")
    #        while True:
    #            yn = input("Do you wish to proceed without a working callback client? (Y/N): ")
    #            if yn.lower() == "n":
    #                stop_running()
    #            elif yn.lower() == "y":
    #                break
    #except errors.CatcherClientConnectionError:
    #    LOG.exception("Client stopped responding")

    # attack phase
    #LOG.info("Starting attack phase")
    #LOG.info("Finished attack phase")
    
    LOG.info("Finished")

if __name__ == '__main__':
    print("Running")
    init_request('127.0.0.1', 9999, './request.txt')
    print("Completed")

