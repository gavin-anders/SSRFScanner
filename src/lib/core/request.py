"""
Created on 5 Jul 2017

@author: gavin
"""
from lib.core import settings
from lib.core.log import CustomLogger
from http.client import HTTPConnection, HTTPResponse
from io import StringIO
from OpenSSL import SSL

import collections
import socket
import datetime
import logging
import hashlib

logging.setLoggerClass(CustomLogger)
LOG = logging.getLogger(settings.APPLICATION)

class RawResponse(HTTPResponse):
    def __init__(self, *args, **kwargs):
        HTTPResponse.__init__(self, *args, **kwargs)
        self.time = None
        self.raw = None

    def __str__(self):
        if self.raw:
            return self.raw
        else:
            return "Unable to render - <lib.core.request.RawResponse instance>"
        
    def _set_resp_time(self, forcetime=None):
        self.time = datetime.datetime.now().microsecond
        if forcetime:
            self.time = forcetime
            
    def _set_raw_response(self):
        if self.raw is None:
            self.raw = self.read()
    
    def read_response(self):
        #response = "{} {} {}\r\n{}\r\n".format(self., self.version, self.self.read())

        self._set_raw_response()
        self._set_resp_time()   #should this be the response time from the request?

    def get_plain_request(self):
        return self.raw.decode("utf-8") 

class SSLConnection(object):
    """
    Taken from https://github.com/shanemhansen/pyopenssl_httplib/blob/master/pyopenssl_httplib.py
    
    Proxy to OpenSSL.SSL.Connection containing support for the .makefile()
    method.
    Rationale: The pyopenssl documentation states that
    OpenSSL.SSL.Connection.makefile raises a NotImplemented error because
    there are no .dup semantics for SSL connections which *is* the documented
    behaviour of of socket.makefile, but the documentation is incorrect.
    See: http://bugs.python.org/issue14303
    We can use the logic in socket._fileobject to implement .makefile(),
    allowing pyopenssl to play nice with python's httplib.
    """
    __slots__ = ["_conn"]

    def __init__(self, ctx, conn):
        self._conn = SSL.Connection(ctx, conn)

    def __getattr__(self, attr):
        return getattr(self._conn, attr)

    def makefile(self, *args):
        return socket._fileobject(self, *args)

class RawRequest(HTTPConnection):
    """
    Represents a single raw request.
    Lets define our own HTTPSConnect code
    host, port=None, strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None
    """
    __all__ = [""]
     
    def __init__(self, host, port, raw, is_ssl=False, proxy=None):
        HTTPConnection.__init__(self, host, port)
        self.response_class = RawResponse
        self.rfile = StringIO(raw)
        self.timeout = settings.DEFAULT_CLIENT_TIMEOUT
        self.method = None
        self.path = None
        self.version = None
        self.data = None
        self.is_ssl = is_ssl
        self.verbose = 0
        self.delay = 0
        self.checksum = None
        self.proxy = proxy
        self.parse_request()
    
    def __key(self):
        return (self.host, self.port, self.rfile)
    
    def __hash__(self):
        return hash(self.__key())
    
    def __eq__(self, other):
        return self.__key() == other.__key()
    
    def __ne__(self, other):
        return self.__key() != other.__key()
        
    def connect(self):
        """
        Overwritten
        Connect to the host and port specified in __init__.
        """       
        def _ssl_verify_callback(connection, x509, errnum, errdepth, ok):
            return True
        
        if self.is_ssl is True:
            try:
                self.sock = socket.create_connection((self.host, self.port), float(self.timeout), self.source_address)
                if self._tunnel_host:
                    self._tunnel()
                LOG.debug("Doing SSL/TLS Connection")
                context = SSL.Context(SSL.SSLv23_METHOD)
                self.sock = SSLConnection(context, self.sock)
                self.sock.set_connect_state()
            except Exception as sslerror:
                LOG.error(sslerror.msg)
        else:
            self.sock = socket.create_connection((self.host, self.port), float(self.timeout), self.source_address)
            if self._tunnel_host:
                self._tunnel()
            
    def parse_request(self):
        LOG.debug("Parsing raw request")
        requestline, rawheaders = self.rfile.getvalue().split('\n', 1)
        self.method, path, self.version = requestline.split(' ', 2)
        # parse data
        if '\n\n' in rawheaders:
            rawheaders, self.data = rawheaders.split('\n\n', 1)

        # Parse headers
        self._parse_headers(rawheaders)
        
        # parse query
        if '#' in path:
            self.path, ignore = path.split('#', 1)
        else:
            self.path = path
            
        s = (self.host + str(self.port) + self.rfile.getvalue()).encode('utf-8')
        self.checksum = hashlib.md5(s).hexdigest()
            
    def _parse_headers(self, rawheaders):
        """
        Parses a raw request headers to ordered dictionary
        """
        self.headers = collections.OrderedDict()
        for line in rawheaders.split('\n'):
            name, value = line.rstrip().split(':', 1)
            self.headers[name] = value.rstrip().lstrip()
            
    def set_verboselevel(self, level=0):
        """
        Turns on verbose within the class, prints raw requests
        """
        self.verbose = level
        
    def validate(self):
        """
        Perform simple validation on request instance. Only basic as we'll likely be breaking rfc
        
        :return    bool    return True if passed validation
        """
        if self.method is not None and self.path is not None and self.version is not None:
            if self.version == 'HTTP/1.1':
                if len(self.get_header('Host')) > 0:
                    return True
            else:
                return True
        return False
    
    def get_header(self, name):
        """
        Get header by name
        
        :param     name: index of header name
        :returns:  header value from header list
        """
        try:
            headername = name.rstrip()
            return self.headers[headername]
        except KeyError:
            return None
        
    def add_header(self, name, value):
        """
        Adds a new header to list, small bit of validation performed
        
        :param    name: header name to overwrite supplied value
        :param    value: value to overwrite current value
        """
        self.headers[name.rstrip()] = value.rstrip()
    
    def add_data(self, data):
        self.data = self.data + data
        self._validate_request()
    
    def set_raw_request(self, raw):
        """
        Create a new raw request from provided details
        
        :param    raw: new raw string
        :return StringIO rawrequest
        """
        raw = StringIO(raw)
        self.rfile = raw
        self.parse_request()
    
    def get_raw_request(self):
        """
        Gets the raw request as a string
        
        :return    string of raw request
        """
        r = "%s %s %s\n" % (self.method, self.path, self.version)
        for h in self.headers:
            r = r + "%s: %s\n" % (h, self.headers[h])
        r = r + "\n"
        r = r + self.data
        r = r + "\n"
        self.rfile = StringIO(r)
        return self.rfile.getvalue()
    
    def set_delay(self, delay):
        """
        Time delay before sending every request
        """
        self.delay = float(delay)
    
    def set_proxy(self, ip, port):
        """
        Reverse the host + port values, with tuple details
        
        :param    proxydetail    tuple - (ip, port)
        """
        self.set_tunnel(self.host, self.port)
        self.host = ip
        self.port = int(port)
        LOG.debug("Using proxy http://{}:{}".format(self.host, self.port))
    
    def send_request(self):
        LOG.debug("Sending {}".format(self.checksum))
        if self.proxy:
            self.set_proxy(self.proxy[0], self.proxy[1])
        self.putrequest(self.method, self.path, skip_host=1, skip_accept_encoding=1)
        
        for h in self.headers:
            self.putheader(h, self.headers[h])
        self.endheaders(message_body=str.encode(self.data)) ########### HERE ###############
        
        #print the request
        LOG.request(self.get_raw_request())
        
        response = self.getresponse()

        LOG.response(response)
            
        # CLose up connection
        self.sock = None
        self.close()
        return response
             
if __name__ == '__main__':
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

"""

    req = RawRequest('127.0.0.1', 9999, raw, is_ssl=False)
    req2 = RawRequest('127.0.0.1', 9998, raw, is_ssl=False)
    req3 = RawRequest('127.0.0.1', 9999, raw, is_ssl=False)
    reqs = [req, req2]
    
    print(req)
    print(req2)
    
    if req3 in reqs:
        print("found req in request list")
    
    req.set_debuglevel(0)
    req.set_verboselevel(1)
    req.set_proxy('127.0.0.1', 8080)
    req.connect()
    resp = req.send_request()
    print("")
    print("Response...")
    print(resp.status)
    print(resp.reason)
    print("Finished")