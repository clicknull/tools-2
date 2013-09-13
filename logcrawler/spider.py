#!/usr/bin/env python
# coding: utf-8

import os
import shutil
import socket
import time
import urllib2
from urlparse import urlparse
from logcrawler import common, rest

LOG = common.get_logger(filename=__file__, topic=__file__)


class Spider(object):
    def __init__(self, root):
        self.root = root
        self._error = None

    def crawl(self, url):
        start = time.time()
        self.handle_crawl_start(url, start)

        result, size, local_path = self._crawl(url)

        end = time.time()
        self.handle_crawl_end(url, start, end, result, size)

        hostname = socket.gethostname()
        ret = locals()
        del ret['self']
        return ret

    def _crawl(self, url):
        """ Crawl target url by HTTP GET.
        """
	
	host  = urlparse(url).netloc.split(":")[0]
        if common.is_ipaddress(host) and common.is_public_IP(host):
	    proxy = {'http': 'http://192.168.111.210:8080'}
            handler = urllib2.ProxyHandler(proxy)
	    opener = urllib2.build_opener(handler)
	    urllib2.install_opener(opener)

        local_path = self.get_local_path(url)
        temp_local_path = local_path + '.tmp'
        try:
            fd_remote = urllib2.urlopen(url, timeout=1)
            with open(temp_local_path, "wb") as fd_local:
                shutil.copyfileobj(fd_remote, fd_local)
        except (urllib2.URLError, socket.error, IOError), err:
            if os.path.exists(temp_local_path):
                os.remove(temp_local_path)
            size = 0
            self._notify_err(err)
            LOG.error(msg="crawl url [%s] error: [%s]" % (url, str(err)))
        else:
            os.rename(temp_local_path, local_path)
            size = os.path.getsize(local_path)
            self._notify_success()

        LOG.info(msg="crawl url [%s] result: [%s]" % (url, self._error))
        
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        urllib2.install_opener(opener)

        return self._error, size, local_path

    def _notify_err(self, err):
        if isinstance(err, urllib2.HTTPError):
            self._error = "httperr"
        elif isinstance(err, urllib2.URLError) or isinstance(err, socket.error):
            self._error = "connecterr"
        elif isinstance(err, IOError):
            self._error = "ioerr"
        else:
            self._error = "Unknown: " + str(err)
 
    def _notify_success(self):
        self._error = "success"

    def get_local_path(self, url):
        if not self.root:
            return None
        # TO BE FIX: join path for test
        try:
            [service, time, fname] = urlparse(url).path.strip('/').split('/')
        except Exception as e:
            LOG.error(msg="get local path error: [%s] [%s]" % (url, str(e)))
            return None
        idc = fname.split('.')[0]
        path = os.path.join(self.root, service, time, idc, fname)
        parent = os.path.dirname(path)
        if not os.path.exists(parent):
            common.makedirs(parent)
        return path
    
    @common.async
    def handle_crawl_start(self, url, start_time):
        """ Call RESTFul API to record crawling start.
        """
        data = dict(url=url, size=0, status='downloading',
            desc=None, start=start_time, end=None)

        # call rest api to get crawling record
        # create a new one if no record found
        # else update crawling status for this record
        items = rest.api_crawl(api='get', target_url=url)
        if len(items) > 0:
            data['id'] = items[0].get('id')
            rest.api_crawl(api='update', target_url=url, post_data=data)
        else:
            rest.api_crawl(api='create', target_url=url, post_data=data)

    @common.async
    def handle_crawl_end(self, url, start_time, end_time, result, size):
        """ Call RESTFul API to record crawling end status.
        """
        # sleep 0.5s to avoid updating status frequently
        time.sleep(0.5)

        if result == "success":
            status, desc = "done", None
        else:
            status, desc = "error", result

        data = dict(url=url, size=size, status=status,
            desc=desc, start=start_time, end=end_time)

        items = rest.api_crawl(api='get', target_url=url)
        if len(items) > 0:
            data['id'] = items[0].get('id')
            rest.api_crawl(api='update', target_url=url, post_data=data)
        else:
            rest.api_crawl(api='create', target_url=url, post_data=data)
