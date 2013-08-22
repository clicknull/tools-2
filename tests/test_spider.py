#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Unit test for spider module
"""

from SimpleHTTPServer import SimpleHTTPRequestHandler
from urlparse import urlparse
import unittest
import shutil
import threading
import SocketServer
import socket
import logging
import urllib2
import time
import os

from logcrawler import spider

SRCPATH = "tmp_src"
DSTPATH = "tmp_dst"
IP = "127.0.0.1"
PORT = 8001

logging.disable(logging.CRITICAL)

class BaseSpiderTestCases(unittest.TestCase):

    class TestSpider(spider.Spider):
        def get_local_path(self, url):
            path = os.path.join(self.root, urlparse(url).path.strip('/'))
            parent = os.path.dirname(path)
            if not os.path.exists(parent):
                os.makedirs(parent)
            return path

    sp = TestSpider(root=DSTPATH)

    def setUp(self):
        if not os.path.exists(SRCPATH):
            os.makedirs(SRCPATH)
        if not os.path.exists(DSTPATH):
            os.makedirs(DSTPATH)
        with open(os.path.join(SRCPATH, "a.txt"), 'w') as f:
            f.write("funshion")

        self.httpd = HTTPServer(SimpleHTTPRequestHandler, IP, PORT)
        self.httpd.start()
        time.sleep(3)

    def tearDown(self):
        shutil.rmtree(SRCPATH)
        shutil.rmtree(DSTPATH)
        self.httpd.join()

    def test_get_local_path(self):
        pass

    def test_crawl(self):
        """ Test crawl method.
        """
        url = "http://localhost:{0}/{1}/a.txt".format(PORT, SRCPATH)
        src_path = os.path.join(SRCPATH, "a.txt")
        dst_path = os.path.join(DSTPATH, SRCPATH, "a.txt")
        src_size = os.path.getsize(src_path)

        ret = self.sp.crawl(url)
        self.assertEqual(ret.get("url"), url)
        self.assertEqual(ret.get("size"), src_size)
        self.assertEqual(ret.get("result"), "success")

    def test_crawl_internal_with_200(self):
        """ _crawl test case.
        """
        url = "http://localhost:{0}/{1}/a.txt".format(PORT, SRCPATH)
        src_path = os.path.join(SRCPATH, "a.txt")
        dst_path = os.path.join(DSTPATH, SRCPATH, "a.txt")
        src_size = os.path.getsize(src_path)

        result, dst_size, local_path = self.sp._crawl(url)
        self.assertTrue(os.path.exists(dst_path))
        self.assertEqual(src_size, dst_size)
        self.assertEqual(result, "success")
        self.assertEqual(local_path.replace('\\', '/'), "{0}/{1}/a.txt".format(DSTPATH, SRCPATH))

    def test_crawl_internal_with_404(self):
        url_404 = "http://localhost:{0}/{1}/b.txt".format(PORT, SRCPATH)
        result, dst_size, local_path = self.sp._crawl(url_404)
        self.assertTrue(result, "httperr")
        self.assertEqual(dst_size, 0)
        self.assertEqual(local_path.replace('\\', '/'), "{0}/{1}/b.txt".format(DSTPATH, SRCPATH))

    def test_crawl_internal_with_timeout(self):
        url_unreached = "http://www.youtube.com/a/a.txt"
        result, dst_size, local_path = self.sp._crawl(url_unreached)
        self.assertTrue(result, "connecterr")
        self.assertEqual(dst_size, 0)

    def test_notify_err(self):
        self.sp._notify_err(None)
        self.assertEqual(self.sp._error, "Unknown: None")

    def test_notify_success(self):
        self.sp._notify_success()
        self.assertEqual(self.sp._error, "success")

class HTTPServer(threading.Thread):
    def __init__(self, handler, ip="", port=8000):
        self.handler = handler
        self.ip = ip
        self.port = port
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)

    def run(self):
        """ Main loop
        """
        socket.setdefaulttimeout(10)
        httpd = SocketServer.TCPServer((self.ip, self.port), self.handler, bind_and_activate=False)
        httpd.allow_reuse_address = True
        try:
            httpd.server_bind()
        except socket.error:
            # sleep 2 minutes if address alread in used
            time.sleep(120)
            httpd.server_bind()
        httpd.server_activate()    
        while not self._stopevent.isSet():
            httpd.handle_request()

    def do_dummy_request(self):
        """ Do a dummy http request to stop service.
        """
        url = "http://%s:%d/" % (self.ip, self.port)
        try:
            response = urllib2.urlopen(url)
        except:
            pass
        else:
            print "HTTP Response: %d" % response.getcode()

    def join(self):
        """ Stop service thread.
        """
        self._stopevent.set()
        self.do_dummy_request()
        threading.Thread.join(self)


if __name__ == "__main__":
    unittest.main()
