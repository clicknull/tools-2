#!/usr/bin/env python
# coding: utf-8
r"""本模块使用分析规则中的正则表达式匹配日志文件的每一行，
    只要匹配其中任意一个就将其打包发送给kafka，kafka的topic是随机选取的

#运行逻辑
#1获取分析表中的正则表达式 及相应的kafka topic
#2将日志内容按行读入内存，根据BLOCK_LINES（300000）为一组分配给一个cpu去处理
#3某个cpu分析一块数据，匹配日志中的每一行，只要匹配任意一个表达式，就将其记录
#   根据记录的匹配行数，以MAX_LINES2KAFKA（500）为一组发送给kafka，topic是随机选取的
#4获取每个cpu分析处理每一块数据的结果，将其上报到rest接口
"""

import binascii
import gzip
import os
import random
import re
import socket
import struct
import sys
import time
import traceback

from multiprocessing import Pool

from logcrawler.conf import config
from logcrawler import common

#日志对象句柄
LOG = common.get_logger(filename=__file__, topic=__file__)
#远端REST接口
RULES_REST_URL = 'http://%s:%s/_logcrawler/logcrawler_rest_api/analyze_process_rules/get/' % (config.REST_HOST, config.REST_PORT)
ANALYZE_REST_URL_CREATE = 'http://%s:%s/_logcrawler/logcrawler_rest_api/analyze/create/' % (config.REST_HOST, config.REST_PORT)
#kafka字段中product request id的缺省值
KAFKA_PRODUCE_REQUEST_ID = 0
#每个CPU一次处理的行数
BLOCK_LINES = 300000
#一次发往kafka的最大条数
MAX_LINES2KAFKA = 500
#主机名，只获取一次
HOSTNAME = socket.gethostname()

restWrapper = common.RestWrapper()

def get_execute_options_by(rules,filename):
    execute_options = []
    for rule in rules:
        #状态不为active，不处理
        if rule['status'] != "active":
            continue
        rule['topic'] = eval(rule['parameters'])['topic']
        rule['filename'] = filename
        if rule['filename'].find("/%s/" % rule['service_name']) == -1:
            continue
        if rule['IDC_name'].lower() != "all" and rule['filename'].find(rule['IDC_name']) == -1 :
            continue
        execute_options.extend([rule['IDC_name'],rule['service_name'],rule['regexp'],rule['dealwith_manner'],rule['topic']])
    return execute_options

def split_strategy(total_lines,block_lines=BLOCK_LINES):
    """将total_lines按照 一块block_lines的数量分成多个块

    对可能的异常进行捕获。

    Args:
        total_lines: 总量
        block_lines: 每块的量

    Returns:
        split_list: 被分割后的字典，格式为[[0,300000],[300000,600000]]
                    取数据时使用半闭半开区间即可，即 [0,300000)
                    如果total_lines小于block_lines，则仅取到[0,total_lines)
                    如果total_lines除以block_lines有余数，则全部放到最后一个块，即[n*block_lines,total_lines) 
    Example:
    from analyze_process_by_regexp import split_strategy
    split_strategy(5)
    split_strategy(1000000)
    split_strategy(1000000, 40000)
    """
    split_list = []
    if total_lines > 0 and block_lines > 0:
        if total_lines < block_lines:
            block_count = 1
        else:
            block_count = int(round(total_lines*1.0/block_lines))
        for counter in range(block_count):
            start = block_lines * counter
            if counter == block_count - 1:
                end = total_lines
            else:
                end = start + block_lines
            split_list.append([start, end])
    return split_list

def readfile2memory(filename):
    """将文件filename的内容读入内存，


    Args:
        filename: gz文件内容
    Returns:
        totallines: 日志中行书
        rawArray: rawArray类型的文件内容

    Example:
    from analyze_process_by_regexp import readfile2memory
    readfile2memory("/tmp/file1")
    """
    file_descriptor = gzip.open(filename)
    content = file_descriptor.readlines()
    return len(content),content

def encode_message(message):
    """将message编码，该函数为git hub开源代码，


    Args:
        message: 消息
    Returns:
        编码后的消息

    Example:
    from analyze_process_by_regexp import encode_message
    encode_message("abcde")
    """
    # <MAGIC_BYTE: char> <CRC32: int> <PAYLOAD: bytes>
    return struct.pack('>B', 0) + \
           struct.pack('>i', binascii.crc32(message)) + \
           message

def encode_produce_request(topic, partition, messages):
    """将message根据topic和partition进行联合编码，该函数为git hub开源代码，


    Args:
        topic: kafka的topic
        partition: kafka的partition
        message: 消息
    Returns:
        编码后的消息

    Example:
    from analyze_process_by_regexp import encode_produce_request
    encode_produce_request("topic",0,"abcde")
    """
    # encode messages as <LEN: int><MESSAGE_BYTES>
    encoded = [encode_message(message) for message in messages]
    message_set = ''.join([struct.pack('>i', len(m)) + m for m in encoded])
    
    # create the request as <REQUEST_SIZE: int> <REQUEST_ID: short> <TOPIC: bytes> <PARTITION: int> <BUFFER_SIZE: int> <BUFFER: bytes>
    data = struct.pack('>H', KAFKA_PRODUCE_REQUEST_ID) + \
           struct.pack('>H', len(topic)) + topic + \
           struct.pack('>i', partition) + \
           struct.pack('>i', len(message_set)) + message_set
    return struct.pack('>i', len(data)) + data

class KafkaProducer:
    """发送kafka消息的生成器，来源于git hub

    Example:
    from analyze_process_by_regexp import KafkaProducer
    kafka_producer = KafkaProducer("1.1.1.1",9092)
    kafka_producer.send(["message1","message2"],"topic")
    """
    def __init__(self, host, port):
        try:
            self.connection = socket.socket()
            self.connection.connect((host, port))
        except:
            LOG.error(msg="catch kafka exception when init ipaddress %s,port %d:\n %s" %
                      (host,port, traceback.format_exc()))
            print traceback.format_exc()
            self.connection = None
    def close(self):
        self.connection.close()
    def send(self, messages, topic, partition = 0):
        self.connection.sendall(encode_produce_request(topic, partition, messages))
        LOG.debug(msg="send %d,with topic %s:" % (len(messages), topic))

def send_messages_to_kafka(messages_list,topic_list,producer):
    """将messages_list，随机选取一个topic，发送到kafka
    
    Args:
        messages_list: 消息列表
        topic_list: 随机选取的topic列表
        kafka_ipaddress: kafka的ip地址，缺省为config.KAKFA_IPADDRESS
        kafka_port: kafka的端口号，缺省为config.KAKFA_PORT
    Returns:
        发送成功：返回successful和topic名称
        发送失败：返回failed和失败原因

    Example:
    from analyze_process_by_regexp import send_messages_to_kafka
    send_messages_to_kafka(["abcde"],["topic1"])
    """
    
    if producer is None:
        return "failed","producer is None"
    if producer.connection is None:
        return "failed","connect failed"
    random_topic = topic_list[random.randint(0,len(topic_list)-1)]
    try:
        producer.send(messages_list, "_%s" % random_topic)
        return "successful",random_topic
    except Exception, error:
        LOG.error(msg="catch kafka exception when send %s:\n %s" %
                (error, traceback.format_exc()))
        return "failed","%s %s" % (error, traceback.format_exc())

def process_content2kafka(content,start,end,regexps,topics,IDC_name="undefined"):
    """content逐行 匹配正则表达式列表regexps中任何一个，随机选取一个topics，发送到kafka
    
    Args:
        content: 消息列表
        start: 索引开始位置
        end: 索引结束位置，不包括该位置
        regexps: 被匹配的正则表达式列表
        topics: 随机选取的topic列表
        
    Returns:
        start：索引开始位置（便于get方法获取结果时，知道位置信息）
        end：索引结束位置，（便于get方法获取结果时，知道位置信息）
        run_information：包含运行信息的字典

    Example:
    from analyze_process_by_regexp import process_content2kafka
    process_content2kafka(["abcde","b"],0,1,["a","b"],["topic1","topic2"])
    """
    
    #保存编译后的正则表达式和正则表达式对象字典
    compiled_regexp = {}
    
    #返回信息字典，记录执行信息，并返回，便于celery调用get方法获取
    run_information = {}
    run_information["start_timestamp"] = time.time()
    run_information["status"] = "done"
    run_information["errorinfo"] = []
    for regexp in regexps:
        try:
            compiled_regexp[regexp] = re.compile(regexp)
        except Exception,error:
            run_information["errorinfo"].append(traceback.format_exc())
    
    #根据协商，一条匹配规则，最多只发送一次，且topic的值可以为任意配置的值。即正则表达式跟topic不一定对应
    #发往kafka的缓冲
    kafka_buffer = []
    matchedlines = 0
    producer = KafkaProducer(config.KAKFA_IPADDRESS, config.KAKFA_PORT)
    for line in content:
        for regexp in regexps:
            try:
                if compiled_regexp[regexp].search(line) is None:
                    error = "not found match"
                else:
                    matchedlines += 1
                    kafka_buffer.append("%s\t%s" % (IDC_name, line))
                    #如果匹配上任意正则表达式则退出
                    break
            except Exception, error:
                run_information["status"] = "error"
                if len(run_information["errorinfo"]) < 3:
                    run_information["errorinfo"].append("%s" % (traceback.format_exc(),))
                LOG.error(msg="error a %s %s" % (error,traceback.format_exc()))
    
    for (_start, _end) in split_strategy(len(kafka_buffer),MAX_LINES2KAFKA):
        status,_ = send_messages_to_kafka(kafka_buffer[_start:_end],topics,producer)
        #为了防止kafka故障，当一次发送失败后，就不再发送
        if status == "failed":
            producer = None

    run_information["matchedlines"] = matchedlines
    run_information["end_timestamp"] = time.time()
    
    if producer is not None and producer.connection is not None:
        try:
            producer.close()
        except Exception,_:
            pass
    
    return start,end,run_information

def analyze_process_by(execute_options,filename):
    
    regexps = []
    topics = []
    asyncresults_handler = []
    total_lines, content = readfile2memory(filename)
    if total_lines == 0:
        LOG.debug(msg="filename %s is empty" % filename)
        return
    LOG.debug(msg="%s total_lines :[%d]" % (filename,total_lines))
    
    for count in range(len(execute_options)/5):
        _,_,regexp,dealwith_manner,topic = execute_options[count*5:count*5+5]
        if dealwith_manner == "sendtokafka":
            regexps.append(regexp)
            topics.append(topic)
        #fix me:对于保存到本地的选项，需要另写分支，暂时无代码
        if dealwith_manner == "onserver":
            pass
    #filename 格式 /data2/web/haproxy_access/2013080609/BeiJing_YiZhuang_CTC_log111_100/BeiJing_ShangDi_CNC_log116_71.201308060925.gz    
    try:
        IDC_name = os.path.basename(filename).split(".")[0]
    except:
        IDC_name = "undefined"

    splitted_list = split_strategy(total_lines,total_lines/len(split_strategy(total_lines)))
    LOG.debug(msg="splitted_list %s " % (splitted_list,))
    pool = Pool(processes=len(splitted_list))
    for (start, end) in splitted_list:
        asyncresults_handler.append(pool.apply_async(process_content2kafka, (content[start:end],start,end,regexps,topics,IDC_name)))
    pool.close()
    pool.join()
    
    path = os.path.basename(filename)
    filesize = os.path.getsize(filename)
    
    #retrieval result and send statistics information.
    for result in asyncresults_handler:
        try:
            if result.successful():
                start,end,run_information = result.get()
                data = {"path": path, 
                       "filesize": filesize, 
                       "filelines": total_lines, 
                       "collector_ip_address": HOSTNAME,
                       "start_timestamp": run_information.get("start_timestamp",time.time()),
                       "end_timestamp": run_information.get("end_timestamp",time.time() ),
                       "status": run_information.get("status","done"),
                       "description": "[%d,%d)=%d,matchedlines=%d,%s" % (start,end,end - start,run_information.get("matchedlines"),regexps),
                       }
                restWrapper.post(ANALYZE_REST_URL_CREATE,data=data)
                LOG.info(msg="%s %d %d[%d,%d)=%d runtime=%ds" % (path,filesize,total_lines,start,end,run_information.get("matchedlines"), run_information.get("end_timestamp")-run_information.get("start_timestamp")))
            else:
                LOG.error(msg="result gets failed")
        except Exception, error:
            LOG.error(msg="%s" % error)

def analyze(filename,rules_rest_url=RULES_REST_URL):
    """获取分析规则，计算执行选项，根据分析规则处理日志
    
    Args:
        filename: 需要处理的日志文件路径名
        rules_rest_url: 获取处理规则的rest地址
        
    Returns:
        无

    Example:
    import analyzer
    analyzer.analyze("/data2/web/haproxy_access/2013080609/BeiJing_YiZhuang_CTC_log111_100/BeiJing_ShangDi_CNC_log116_71.201308060925.gz")
    """
    LOG.info(msg="start analyze %s" % (filename,))
    json_content = restWrapper.get(rules_rest_url,timeout=5)
    LOG.debug(msg="json_content length %d" % len(json_content))

    rules = json_content.get('rule',[])
    LOG.debug(msg="rules length %d" % len(rules))

    execute_options = get_execute_options_by(rules,filename)
    LOG.debug(msg="execute_options length %d" % len(execute_options))
    analyze_process_by(execute_options,filename)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >> sys.stderr, 'USAGE: python', sys.argv[0], 'gz_filename'
        sys.exit(1)
    else:
        analyze(sys.argv[1])
