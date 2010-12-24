#!/usr/bin/env python
# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.


from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class DropHandler(BaseHTTPRequestHandler):
    def dropRequest(self):
        self.send_response(200)
        self.send_header('Content-length', '0')
        self.send_header('Connection', 'close')
        self.end_headers()
    do_GET = do_POST = do_HEAD = do_PURGE = do_OPTIONS = do_PUT = do_DELETE = do_TRACE = do_CONNECT = dropRequest
        
def main():
    server = HTTPServer(('', 8989), DropHandler)
    server.serve_forever()

    
if __name__ == '__main__':
    main()
