#!/usr/bin/env python
#coding: UTF-8

r"""本模块探测机房服务状态表中所指示服务对应文件的存在性，
    根据该存在性，修改机房对应服务的运行状态
#运行逻辑
#1获取机房 服务 状态表
#2计算远端url
#3探测url的存在性（返回200）
# 根据探测小时数计算探测点数
#4修改状态
# 如果当前online 且都不存在 则置offline
# 如果当前offline 若探测的有一个存在，则置online
"""

import datetime
import requests
import time

from logcrawler.conf import config
from logcrawler import common

logger = common.get_logger(filename=__file__, topic=__file__)
IDC_COLLECT_REST_URL_UPDATE = "http://%s:%s/_logcrawler/logcrawler_rest_api/IDC_collect/update/" % (config.REST_HOST, config.REST_PORT)
#探测距离当前时间最大小时
MAX_HOURS = 2
#探测距离当前时间最大分钟数
MAX_MINUTES = 10

def get_files(text):
    """返回text中的的文件名列表
    Args:
        text: 包含文件名信息的文本（通过http获取的文件信息）

    Returns:
        files: text中文件名列表 
    Example:
    from analyze_process_by_regexp import get_files
    get_files('<a href="BeiJing_YiZhuang_CTC_log111_100.201308121058.gz">BeiJing_YiZhuang_CTC_log111_100.201308121058.gz</a>    12-Aug-2013 10:59           108074817
<a href="BeiJing_YiZhuang_CTC_log111_100.201308121059">BeiJing_YiZhuang_CTC_log111_100.201308121059</a>       12-Aug-2013 10:59           527771479
</pre><hr></body>
</html>')
    #返回["BeiJing_YiZhuang_CTC_log111_100.201308121058.gz","BeiJing_YiZhuang_CTC_log111_100.201308121059"]
    """
    files = []
    for line in text.split('\n'):
        try:
            _,href,_,_,_ = line.split()
            filename = href.split("\"")[1]
            files.append(filename)
        except:
            pass
    return files

def update_idc_current_status():
    idc_config_url = config.IDC_CONFIG_URL_FORMAT % {"IP": config.REST_HOST, "PORT": config.REST_PORT}
    logger.info(msg="getting json from %s" % idc_config_url)
    restWrapper = common.RestWrapper()
    response_json = restWrapper.get(idc_config_url)

    logger.info(msg="get json content %s" % [response_json, ])
    logger.info(msg="get json content len %d" % len(response_json))
    idc_collects = response_json.get("idc_collect",[])
    logger.debug(msg="idc_collects = %s" % (idc_collects,))
    for idc_collect in idc_collects:
        #{u'status': u'active', u'description': u'\u5e7f\u897f-\u5357\u5b81\u65b0-\u7535\u4fe1', u'timestamp': u'2013-06-20 15:53:45', u'IDC_ip_address_port': u'113.17.170.165:80', u'current_status': u'online', u'IDC_name': u'GuangXi_NanNingNew_CTC_LOG_165', u'max_delay_minutes': 5, u'delay_minutes': 2, u'service_name': u'haproxy_access', u'collect_interval_minutes': 0, u'id': 4}
        logger.debug(msg="idc_collect = %s" % (idc_collect,))
        if idc_collect["IDC_ip_address_port"] == "0.0.0.0:0" or idc_collect["IDC_name"] == "all":
            continue
        #记录MAX_HOURS内存在的文件列表
        existed_files = {}
        #记录响应时间
        response_times = []
        for delta_hours in range(MAX_HOURS):
            date = datetime.datetime.now() - datetime.timedelta(hours=delta_hours)
            #file_url format http://222.35.250.18:8080/haproxy_access/2013080616/
            url = "http://%s/%s/%s/" % (idc_collect["IDC_ip_address_port"],idc_collect["service_name"],date.strftime("%Y%m%d%H"),)
            start = time.time()
            try:
                response = requests.get(url,timeout=2)
                response_times.append(time.time() - start)
                for filename in get_files(response.text):
                    existed_files[filename] = True
            except:
                response_times.append(time.time() - start)

                
        if response_times == []:
            response_times = [0.0]
        logger.info("access %s [%f %f]" % (idc_collect["IDC_name"],min(response_times),max(response_times)))
        #统计MAX_MINUTES内文件存在的个数
        #探测成功的计数器
        counter = 0
        for delta_minutes in range(MAX_MINUTES):
            date = datetime.datetime.now() - datetime.timedelta(minutes=delta_minutes)
            filename = "%s.%s.gz" % (idc_collect["IDC_name"],date.strftime("%Y%m%d%H%M"))
            if filename in existed_files:
                counter += 1
        # 如果当前online 且 都不存在 则置offline
        # 如果当前offline 若探测的有一个存在，则置online
        modified_current_status = ""
        if idc_collect["current_status"] == "offline" and counter !=0:
            modified_current_status = "online"
        if idc_collect["current_status"] == "online" and counter == 0:
            modified_current_status = "offline"
        if "" != modified_current_status:
            idc_collect["current_status"] = modified_current_status
        
        descriptions = idc_collect["description"].split("|")
        idc_collect["description"] = "[%f,%f]|%s" % (min(response_times),max(response_times),descriptions[-1])
        logger.info(msg="before post idc_collect %s" % (idc_collect))
        logger.info(msg="post %s to %s" % (idc_collect,IDC_COLLECT_REST_URL_UPDATE))
        response_json = restWrapper.post(IDC_COLLECT_REST_URL_UPDATE,data=idc_collect)
        if len(response_json) != 0 and response_json.get("status","") == "ok":
            logger.info(msg="successfully. %s" % response_json)
        else:
            logger.error(msg="failed. %s" % (response_json,))

if __name__ == "__main__":
    update_idc_current_status()