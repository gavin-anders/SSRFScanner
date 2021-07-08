# encoding: utf-8
'''
@author:     Gavin Anders

@contact:    gavin.anders@googlemail.com
'''

from lib.core import settings
from lib.core.base import main
from lib.core.client import CatcherClient
from lib.core.validators import validate_ip
from lib.core.validators import validate_port
from lib.core.validators import validate_proxy
from lib.core.log import setup_logging
from lib.core.log import CustomLogger

import argparse
import logging
import sys

logging.setLoggerClass(CustomLogger)
LOG = logging.getLogger(settings.APPLICATION)

def validate_args(args):
    try:
        ip, p = args.IP[0].split(':')
        port = int(p)
        
        if validate_ip(ip) is False:
            parser.error("Invalid IP address supplied")
            
        if validate_port(port) is False:
            parser.error("Invalid TCP port supplied")
            
        if args.PROXY:
            if validate_proxy(args.PROXY) is False:
                parser.error("Invalid proxy value. Try 127.0.0.1:1080")

        if args.OOB is True:
            #check OOB is working
            if validate_ip(settings.CATCHER_IP) is False:
                parser.error("Invalid IP address supplied for catcher client")
                args.OOB = False
            if validate_port(settings.CATCHER_PORT) is False:
                parser.error("Invalid port supplied for catcher client")
            c = CatcherClient(settings.CATCHER_IP, settings.CATCHER_PORT, settings.CATCHER_USER, settings.CATCHER_PASS)
            if c.check_connection() is False:
                parser.error("Client catcher connection failed. Check settings.py")
        
        return (ip, port)
    except ValueError:
        parser.error("Invalid TARGET. Try IP_ADDRESS:PORT")
    except Exception as e:
        parser.error(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SSRF enumeration and exploitation tool.')
    parser.add_argument('-v', '--verbose', dest='VERBOSE', action="store", type=int, default=0,
                        help='print debug details to stdout')
    parser.add_argument('--version', action="version", version='%(prog)s ' + settings.VERSION,
                        help='Show the program version number')
    
    parser.add_argument('IP', action="store", nargs=1, type=str,
                    help='the IP and PORT details to target. <IP_ADDRESS:PORT>')
    
    targetgroup = parser.add_argument_group('Target', description='At least one of these options has to be provided to define the target.')
    targetgroup.add_argument('-r', dest='REQUESTFILE', action="store", type=argparse.FileType('r'), required=True,
                             help='Raw HTTP request with file.')
    targetgroup.add_argument('-p', dest='PARAMETER', action="store",
                             help='The parameter to tamper with.')
    targetgroup.add_argument('--proxy', dest='PROXY', action="store",
                             help='Proxy request through HTTP proxy')
    targetgroup.add_argument('--force-ssl', dest='SSL', action="store_true", default=False,
                             help='Force the use of SSL.')
    
    detectgroup = parser.add_argument_group('Detection', description='Methods of detection.')
    detectgroup.add_argument('--content', dest='CONTENT', action="store_true", default=False,
                             help='Look for difference in content')
    detectgroup.add_argument('--error', dest='ERROR', action="store_true", default=False,
                             help='Look for specific error message in response')
    detectgroup.add_argument('--resp', dest='RESPCODE', action="store_true", default=False,
                             help='Look for specific HTTP status code')
    detectgroup.add_argument('--time', dest='TIME', action="store_true", default=False,
                             help='Detect difference in time of responses')
    detectgroup.add_argument('--oob', dest='OOB', action="store_true", default=False,
                             help='Detect out of band communication')
    
    #attackgroup = parser.add_argument_group('Attacks', description='Choose an attack method.')
    #attackgroup.add_argument('--port-scan', dest='PORTSCAN', action="store_true", default=False,
    #                         help='Port scan internal IP range')
    #attackgroup.add_argument('--outbound', dest='OUTBOUND', action="store_true", default=False,
    #                         help='Enumerate allowed egress traffic')
    #attackgroup.add_argument('--aws', dest='AWS', action="store_true", default=False,
    #                         help='Retrieve the AWS EC2 metadata')
    #attackgroup.add_argument('--ntlm', dest='NTLM', action="store_true", default=False,
    #                         help='Attempt a retrieve NetNTLM if running Windows.')
    #attackgroup.add_argument('--files', dest='FILES', action="store_true", default=False,
    #                         help='Attempt a retrieve files from the attack vector.')
    #attackgroup.add_argument('--rebind', dest='REBIND', action="store_true", default=False,
    #                         help='Carry out a DNS rebind attack.')
    #attackgroup.add_argument('--ftp-port', dest='FTPPORT', action="store_true", default=False,
    #                         help='Attempt to punch a hole in the firewall using FTP PORT command and stream injection.')
    #attackgroup.add_argument('--smuggle', dest='SMUGGLE', action="store_true", default=False,
    #                         help='Attempt to abuse identified vector to send unintended protocol.')
    
    generalgroup = parser.add_argument_group('General')
    generalgroup.add_argument('--update', dest='UPDATE', action="store_true",
                              help='download the latest version from Git')

    print(settings.NAME)
    print(settings.DESCRIPTION)
    
    try:
        args = parser.parse_args()
        setup_logging(args.VERBOSE)
        LOG.info("Started {} - {}".format(settings.APPLICATION, settings.VERSION))
        ip, port = validate_args(args)
        main(ip, port, args)
    except IOError as msg:
        parser.error(str(msg))
    except KeyboardInterrupt:
        print("Forced exit! :(")
