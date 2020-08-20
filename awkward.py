#!/usr/bin/env python
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import ssl
import urllib
import subprocess

# server
bindHost = 'localhost'
serverPort = 11911

env = {
    'bind': 'localhost',
    'port': 9801,
    'source': '.',
    'include': '*',
    'separator': '',
    'tls': False,
    'cert': './cert/awkward.crt',
    'key': './cert/awkward.key',
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
        print('=== configuration ===')
        for k in env:
            print(k + ':\t' + str(env[k]))

    return


class AwkwardServer(BaseHTTPRequestHandler):
    def do_GET(self):
        #result = subprocess.run(["cat data.csv | awk -F ',' '{ print $2 }'"], shell=True, stdout=subprocess.PIPE)

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
        length = len(result.stdout)
        if isEnabled('verbose'):
            print(result.stdout.decode('utf-8', errors='ignore'))
            print('Length: ' + str(length))

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-length", length)
        self.end_headers()
        self.wfile.write(result.stdout)
        #self.wfile.write(bytes("<html><head><title>Awkward</title></head><body>", "utf-8"))
        #self.wfile.write(bytes("<p>Request: %s</p><hr><pre>" %self.path, "utf-8"))
        #self.wfile.write(result.stdout)
        #self.wfile.write(bytes("</pre></body></html>", "utf-8"))

if __name__ == '__main__':
    print('Awkward v0.1')
    configure()

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
