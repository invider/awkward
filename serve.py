#!/usr/bin/env python
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import ssl
import subprocess

# server
bindHost = 'localhost'
serverPort = 11911
cert = './cert/awkward.crt'
key = './cert/awkward.key'

env = {
    'source': '.',
}

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
        print(str(env))

    return


class AwkwardServer(BaseHTTPRequestHandler):
    def do_GET(self):
        #result = subprocess.run(["cat data.csv | awk -F ',' '{ print $2 }'"], shell=True, stdout=subprocess.PIPE)

        # form a query
        q = "find " + env['source'] + " -type f -exec cat {} +"

        result = subprocess.run([q], shell=True, stdout=subprocess.PIPE)
        length = len(result.stdout)
        if isEnabled('verbose'):
            print(result.stdout.decode('utf-8', errors='ignore'))
            print('Length: ' + str(length))

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        #self.send_header("Content-length", length)
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Awkward</title></head><body>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p><hr><pre>" %self.path, "utf-8"))
        self.wfile.write(result.stdout)
        self.wfile.write(bytes("</pre></body></html>", "utf-8"))

if __name__ == "__main__":
    configure()

    # setup https server
    httpd = HTTPServer((bindHost, serverPort), AwkwardServer)
    httpd.socket = ssl.wrap_socket(httpd.socket,
                    server_side = True,
                    certfile = cert,
                    keyfile = key,
                    ssl_version = ssl.PROTOCOL_TLS)
    print("Server is listening at https://%s:%s" % (bindHost, serverPort))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print("...Server stopped!")
