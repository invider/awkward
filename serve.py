#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
import ssl
import time
import subprocess

bindHost = 'localhost'
serverPort = 11911
cert = './cert/awkward.crt'
key = './cert/awkward.key'

class AwkwardServer(BaseHTTPRequestHandler):
    def do_GET(self):
        result = subprocess.run(["cat data.csv | awk -F ',' '{ print $2 }'"], shell=True, stdout=subprocess.PIPE)
        print('awk')
        print(result.stdout.decode('utf-8'))
        print('------------')

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Awkward</title></head><body>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p><hr><pre>" %self.path, "utf-8"))
        self.wfile.write(result.stdout)
        self.wfile.write(bytes("</pre></body></html>", "utf-8"))



#if __name__ == "__main__":

# setup https server
httpd = HTTPServer((bindHost, serverPort), AwkwardServer)
httpd.socket = ssl.wrap_socket(httpd.socket,
                server_side = True,
                certfile = cert,
                keyfile = key,
                ssl_version = ssl.PROTOCOL_TLS)
print("Server listening at http://%s:%s" % (bindHost, serverPort))

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass

httpd.server_close()
print("Server stopped.")

