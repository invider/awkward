#!/usr/bin/env python
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys
import ssl
import secrets
import urllib
import subprocess

# server
bindHost = 'localhost'
serverPort = 11911

env = {
    # server options
    'bind': 'localhost',
    'port': 9801,
    # db options
    'source': '.',
    'include': '*',
    'separator': '',
    # security options
    'auth': False,
    'tls': False,
    'cert': './cert/awkward.crt',
    'key': './cert/awkward.key',
    'xtokenFile': './awkward.xtoken',
}

def option(key):
    if key in env:
        return env[key]
    else:
        return ''

def isEnabled(key):
    if key in env and env[key] == True:
        return True
    else:
        return False

def isDisabled(key):
    if key in env and env[key] == True:
        return False
    else:
        return True

def configure():
    key = ''
    n = len(sys.argv)
    for i in range(1,n):
        opt = sys.argv[i]

        if opt == '-v' or opt == '--verbose':
            env['verbose'] = True
        elif opt == '-s' or opt == '--source':
            key = 'source'
        elif opt == '-i' or opt == '--include':
            key = 'include'
        elif opt == '-f' or opt == '--separator':
            key = 'separator'
        elif opt == '-b' or opt == '--bind':
            key = 'bind'
        elif opt == '-p' or opt == '--port':
            key = 'port'
        elif opt == '-t' or opt == '--tls':
            env['tls'] = True
        elif opt == '-c' or opt == '--cert':
            key = 'cert'
        elif opt == '-k' or opt == '--key':
            key = 'key'
        elif opt == '-x' or opt == '--auth':
            env['auth'] = True
        else:
            if opt.startswith('-'):
                raise ValueError('Unknown option [' + opt + ']!')
            elif key != '':
                env[key] = opt
                key = ''
            else:
                raise ValueError('Illegal argument [' + opt + ']!')
    # check if there is a key expecting a value
    if key != '':
        raise ValueError('Value for [' + opt + '] is expected')

    if isEnabled('verbose'):
        print('===== configuration =====')
        for k in env:
            print(k + ':\t' + str(env[k]))
        print('=========================')

    return

def readToken():
    path = option('xtokenFile')
    if os.path.isfile(path):
        if isEnabled('verbose'):
            print('reading access token cached in [' + path + ']')
        with open(path, 'r') as f:
            data = f.read()
        return data.strip()
    else:
        return ''

def setupToken():
    if isDisabled('auth'):
        return

    fresh = False

    xtoken = readToken()
    if xtoken == '':
        # generate a new access token
        if isEnabled('verbose'):
            print('generating new access token')
        xtoken = secrets.token_urlsafe(16)
        fresh = True

    env['xtoken'] = xtoken
    print('Access Token: [' + xtoken + ']')

    if fresh:
        # cache the generated access token
        path = option('xtokenFile')
        with open(path, 'w') as f:
            if isEnabled('verbose'):
                print('caching access token to [' + path + ']')
            f.write(xtoken)
            f.close()


def authenticate(headers):
    if isDisabled('auth'):
        return True

    if not 'X-Token' in headers:
        if isEnabled('verbose'):
            print('Access Denied! No "X-Token" in headers!')
        return False

    xtoken = headers['X-Token']
    if (xtoken == env['xtoken']):
        return True
    else:
        if isEnabled('verbose'):
            print('Access Denied! [' + xtoken + '] != [' + env['xtoken'] + ']')
        return False


class AwkwardServer(BaseHTTPRequestHandler):

    def deny(self):
        self.send_response(401)
        self.end_headers()
        self.wfile.write(bytes("ACCESS DENIED!", "utf-8"))

    def auth(self):
        auth = authenticate(self.headers)
        if not auth:
            self.deny()
            return False
        else:
            return True

    def OK(self, data):
        length = len(data)
        if isEnabled('verbose'):
            print(data.decode('utf-8', errors='ignore'))
            print('Length: ' + str(length))

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-length", length)
        self.end_headers()
        self.wfile.write(data)


    def do_GET(self):
        if not self.auth():
            return

        url = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(url.query)

        query = ''
        if 'q' in qs:
            if len(qs['q']) > 0:
                query = qs['q'][0]

        # form a query
        q = ("find " + option('source') + " -type f -name '" +
                    option('include') + "' -exec cat {} +")

        if len(query) > 0:
            if isEnabled('verbose'):
                print('AWK: [' + query + ']')
            q += " | awk "
            fs = option('separator')
            if fs != '':
                q += " -F\\" + fs
            q += " '" + query + "'"

        result = subprocess.run([q], shell=True, stdout=subprocess.PIPE)
        self.OK(result.stdout)

    def do_POST(self):
        if not self.auth():
            return

        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        query = data.decode('utf-8')


        # form a query
        q = ("find " + option('source') + " -type f -name '" +
                    option('include') + "' -exec cat {} +")

        if len(query) > 0:
            if isEnabled('verbose'):
                print('AWK: [' + query + ']')
            q += " | awk "
            fs = option('separator')
            if fs != '':
                q += " -F\\" + fs
            q += " '" + query + "'"

        result = subprocess.run([q], shell=True, stdout=subprocess.PIPE)
        self.OK(result.stdout)


if __name__ == '__main__':
    print('Awkward v0.1')
    configure()
    setupToken()

    # setup http server
    protocol = 'http'
    httpd = HTTPServer((option('bind'), option('port')), AwkwardServer)

    if isEnabled('tls'):
        protocol = 'https'
        if isEnabled('verbose'):
            print('== using https/tls ==')
            print('private key: ' + env['key'])
            print('certificate: ' + env['cert'])
        httpd.socket = ssl.wrap_socket(httpd.socket,
                        server_side = True,
                        certfile = env['cert'],
                        keyfile = env['key'],
                        ssl_version = ssl.PROTOCOL_TLS)

    print("Awkward start at %s://%s:%s" % (protocol, env['bind'], env['port']))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print("...Server stopped!")
