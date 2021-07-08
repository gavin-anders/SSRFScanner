from lib.core.log import CustomLogger
from lib.core.enums import ERROR_MESSAGES
from lib.core import settings

import logging
import re
import time

logging.setLoggerClass(CustomLogger)
LOG = logging.getLogger(settings.APPLICATION)

def detect_content_difference(orig, resp, withheaders=False):
    """
    A simple detection if there is a difference in response content sizes
    """
    LOG.debug("Checking difference in content size")
    upercsize = len(orig.raw) + int(round(len(orig.raw)) * 0.1)
    lpercsize = len(orig.raw) - int(round(len(orig.raw)) * 0.1)
    if len(resp.raw) > upercsize:
        LOG.debug("Response length was over 10% larger")
        return True
    if len(resp.raw) < lpercsize:
        LOG.debug("Response length was over 10% smaller")
        return True
    return False

def detect_time_difference(orig, resp):
    """
    Detect the difference in time
    """
    LOG.debug("Checking difference in response times")
    if resp.time > orig.time and resp.time > settings.AVG_RESP_TIME:
        LOG.debug("Response time took longer than the average response time and original request time")

def detect_code_difference(orig, resp):
    """
    Compare the difference in HTTP status codes
    """
    LOG.debug("Checking difference in HTTP response codes")
    if resp.status != orig.status:
        LOG.debug("Manipulated response has a HTTP status code of {}".format(resp.status))
        return True
    return False

def detect_oob(orig, resp, client=None):
    """
    Detect if a call was made externally
    """
    LOG.debug("Checking for an OOB call")
    # check with external callback client
    if client.check_connection() is True:
        # we need to set proxy details here
        LOG.debug("Time sleep - waiting for a callback")
        time.sleep(settings.CALLBACK_WAIT_TIME)
        if client.check_connection() is True:
            for ip in iplist:
                LOG.debug("Looking for callbacks from {}".format(ip))
                callbacks = client.get_callback_by_source(ip=ip)

def detect_error_messages(resp):
    """
    Looks for a known error in the response
    """
    LOG.debug("Checking for errors in the response")
    for erritem in ERROR_MESSAGES:
        search = erritem["search"]
        r = re.search(search, resp.get_plain_request(), re.IGNORECASE)
        if r:
            LOG.debug("'{}' - Error message detected!".format(erritem["name"]))
            return erritem
    return None