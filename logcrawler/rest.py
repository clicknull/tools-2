#!/usr/bin/env python
# coding: utf-8

import socket
import json
import logging
import requests
from requests.exceptions import ConnectionError, HTTPError

from logcrawler.conf.config import REST_HOST, REST_PORT

HOSTNAME = socket.gethostname()
REST_ADDR = ':'.join([REST_HOST, REST_PORT])


def api_crawl(api, target_url, post_data=None):
    """ Call RESTFul API of crawling progress.

        Args:
            api: API type, include get, create and update.
            target_url: Crawling url.
            post_data: Directory of api parameters, just for CREATE and UPDATE.

        Return:
            Deserialized api response.

        Example:
            >>> api_crawl('get', 'http://host/path/a.gz')
            [{'id':1,'url':'http://host/path/a.gz','filesize':15354,
              'collector_ip_address':'192.168.111.212','start_timestamp':1370661142.123,
              'end_timestamp':1370661204.345,'status':'downloading'}]
    """
    if api.lower() not in ['get', 'create', 'update']:
        raise ValueError('api_crawl'+api)

    if api == 'get':
        return _api_crawl_get(target_url)
    if api == 'create':
        return _api_crawl_create(**post_data)
    if api == 'update':
        return _api_crawl_update(**post_data)

def _api_crawl_get(url):
    api_url = 'http://%s/_logcrawler/logcrawler_rest_api/download/get/' % REST_ADDR
    query = {'url_include': url}

    try:
        response = requests.get(url=api_url, params=query)
        response.raise_for_status()
    except (ConnectionError, HTTPError), error:
        logging.error(msg='Crawl get request error: [%s]' % str(error))
        return []
        
    data = response.json()
    records = data['download'] if data['status'] == 'ok' else []

    logging.debug(msg="Crawl get request [%s]" % api_url)
    logging.debug(msg="Crawl get response [%s]" % str(records))
    
    return records

def _api_crawl_create(url, size, status, desc, start, end):
    api_url = 'http://%s/_logcrawler/logcrawler_rest_api/download/create/' % REST_ADDR
    post_data = {
        'url': url,
        'filesize': size,
        'start_timestamp': start,
        'end_timestamp': end,
        'status': status,
        'description': desc,
        'collector_ip_address': HOSTNAME,
    }
    headers = {'content-type': 'application/json'}

    try:
        response = requests.post(url=api_url, data=json.dumps(post_data), headers=headers)
        response.raise_for_status()
    except (ConnectionError, HTTPError), error:
        logging.error(msg='Crawl create request error: [%s]' % str(error))
        return None

    data = response.json()
    id = data['id'] if data['status'] == 'ok' else None

    logging.debug(msg="Crawl create request [%s]" % api_url)
    logging.debug(msg="Crawl create response [%s]" % str(id))

    return id

def _api_crawl_update(url, size, status, desc, start, end, id):
    api_url = 'http://%s/_logcrawler/logcrawler_rest_api/download/update/' % REST_ADDR
    post_data = {
        'id': id,
        'url': url,
        'filesize': size,
        'start_timestamp': start,
        'end_timestamp': end,
        'status': status,
        'description': desc,
        'collector_ip_address': HOSTNAME,
    }
    headers = {'content-type': 'application/json'}

    try:
        response = requests.post(url=api_url, data=json.dumps(post_data), headers=headers)
        response.raise_for_status()
    except (ConnectionError, HTTPError), error:
        logging.error(msg='Crawl update request error: [%s]' % str(error))
        return None

    logging.debug(msg="Crawl update request [%s]" % api_url)
    logging.debug(msg="Crawl update response [%s]" % response.json()['status'])
