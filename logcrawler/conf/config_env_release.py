# -*- coding: utf-8 -*-
# URL format of crawling task for spider 
TASK_SRC_FMT = "http://%(IDC_ip_address_port)s/%(service_name)s/%(YYYYmmddHH)s/%(IDC_name)s.%(YYYYmmddHHMM)s.gz"

# IP:PORT address for RESTFul API  
REST_HOST = '192.168.111.214'
REST_PORT = '80'

# CELERY BROKER & BACKEND URL
CELERY_BROKER  = 'amqp://celeryu:celeryp@192.168.111.214:5673/celeryh'
CELERY_BACKEND = 'amqp://guest@192.168.111.214:5673//'

# Django database settings
DB_HOST = '192.168.111.220'
DB_PORT = '3306'

#kafka server的ip地址和端口号
KAKFA_IPADDRESS = "192.168.111.215"
KAKFA_PORT = 9092

