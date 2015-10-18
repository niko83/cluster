#!/usr/bin/env python
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
import multiprocessing.pool
import json
from gravity import make_cluster
import traceback


class ThreadPoolWSGIServer(WSGIServer):

    def __init__(self, thread_count=None, *args, **kwargs):
        '''If 'thread_count' == None, we'll use multiprocessing.cpu_count() threads.'''
        WSGIServer.__init__(self, *args, **kwargs)
        self.thread_count = thread_count
        self.pool = multiprocessing.pool.ThreadPool(self.thread_count)

    # Inspired by SocketServer.ThreadingMixIn.
    def process_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
            self.shutdown_request(request)
        except:
            self.handle_error(request, client_address)
            self.shutdown_request(request)

    def process_request(self, request, client_address):
        self.pool.apply_async(self.process_request_thread, args=(request, client_address))


def make_server(host, port, app, thread_count=None, handler_class=WSGIRequestHandler):
    httpd = ThreadPoolWSGIServer(thread_count, (host, port), handler_class)
    httpd.set_app(app)
    return httpd


def application(environ, start_response):
    try:
        if environ['QUERY_STRING']:
            data = [float(i.strip()) for i in environ['QUERY_STRING'].split(',') if i.strip()]
        else:
            try:
                data = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))
            except (TypeError, ValueError):
                raise
            data = json.loads(data)
        output = make_cluster(data, save_img=True, make_hist=False)
    except Exception as e:
        traceback.print_exc()
        output = data

    start_response("200 OK", [('Content-Type', 'application/json')])
    return [json.dumps(output)]


httpd = make_server('', 8004, application)
httpd.serve_forever()
