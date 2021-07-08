'''
Created on 12 Feb 2018

@author: gavin
'''
import logging
import os
import sys
import socket

'''
Global variables
'''
NAME = '''

  ____ ____  ____  _____   ____                  
 / ___/ ___||  _ \|  ___| / ___|  ___ __ _ _ __  
 \___ \___ \| |_) | |_    \___ \ / __/ _` | '_ \ 
  ___) |__) |  _ <|  _|    ___) | (_| (_| | | | |
 |____/____/|_| \_\_|     |____/ \___\__,_|_| |_|
                                                 

'''
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
APPLICATION = "ssrf-scan"
DESCRIPTION = "Automated SSRF detection and exploitation tool."
AUTHOR = "Gavin Anders"
VERSION_NUM = "0.1"
APPLICATION_URL = ""
STABLE_VERSION = False
PYTHON_VERSION = "Test"
if STABLE_VERSION:
    VERSION = "v" + VERSION_NUM[:3] + "-stable"
else:
    VERSION = "v" + VERSION_NUM[:3] + "-dev#" + VERSION_NUM[4:]

GIT_URL = ""
DEFAULT_CONFIG = os.path.join(BASE_DIR, 'config.ini')

'''
Request Settings
'''
TEST_PARAMETER = ""
USER_POST_DATA = ""
USER_HOST_HEADER = ""
USER_COOKIE = ""
USER_HEADERS = ""
DEFAULT_USER_AGENT = APPLICATION + "/" + VERSION
FORCE_SSL = False
DEFAULT_CLIENT_TIMEOUT = 10.0
NUM_CHECKS = 3

'''
HTTP Proxy Settings
'''
HTTP_PROXY_HOST = ""
HTTP_PROXY_PORT = 8080

'''
Injection Settings
'''
REPLACE_STRINGREPLACE_IP_STRING = '$IP$'

'''
Detection Settings
'''
AVG_RESP_TIME = 3000000 #microseconds
CALLBACK_WAIT_TIME = 0.5

'''
Attack Settings
'''
PORT_SCAN_ATTACK = False
OUTBOUND_ATTACK = False
AWS_ATTACK = False
NTLM_ATTACK = False
FILES_ATTACK = False
REBIND_ATTACK = False
PROXY_ATTACK = False

'''
Project settings
'''


'''
Log Settings
'''
LOG_LEVEL = logging.INFO
LOG_MAX_BYTES = 100000
LOG_FILE_ROTATE = 5
LOG_NAME = 'debug.log'
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_PATH = os.path.join(LOG_DIR, LOG_NAME)

if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except OSError:
        sys.exit('Error: failed to write to log directory ' + str(LOG_DIR))

'''
Callback Catcher settings
'''
#CATCHER_IP = '18.221.124.159'    #this needs to be an ip
CATCHER_IP = '127.0.0.1'
CATCHER_PORT = 12444
CATCHER_USER = 'admin'
CATCHER_PASS = 'password'
POLL_SEC = 30
CATCHER_DOMAIN = "pentestlabs.uk"
