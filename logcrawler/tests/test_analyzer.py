#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Unit test for analyzer module
"""
import gzip
import os.path
import shutil
import logging
import unittest

from logcrawler.analyzer import *

logging.disable(logging.CRITICAL)

TMPPATH = "tmp"

class AnalyzerTestCases(unittest.TestCase):

    def setUp(self):
        if not os.path.exists(TMPPATH):
            os.makedirs(TMPPATH)

    def tearDown(self):
        shutil.rmtree(TMPPATH)
        
    def test_split_strategy_valid(self):
        """测试analyzer.split_strategy(), 处理正常数据, 预期结果: 返回预期结果
        """
        self.assertEqual(split_strategy(1,1),[[0,1]], "")
        self.assertEqual(split_strategy(1,2),[[0,1]], "")
        self.assertEqual(split_strategy(2,1),[[0,1],[1,2]], "")
        self.assertEqual(split_strategy(2,2),[[0,2]], "")
        self.assertEqual(split_strategy(3,2),[[0, 2],[2, 3]], "")
        self.assertEqual(split_strategy(17,7),[[0, 7],[7, 17]], "")
        self.assertEqual(split_strategy(17,6),[[0, 6],[6, 12],[12, 17]], "")
        self.assertEqual(split_strategy(0,6),[], "")
        
    def test_split_strategy_invalid(self):
        """测试analyzer.split_strategy(), 处理异常数据, 预期结果: 返回空
        """
        self.assertEqual(split_strategy(-1,20),[], "-1,20")
        self.assertEqual(split_strategy(10,-1),[], "10,-1")
        self.assertEqual(split_strategy(10,0),[], "10,0")
        
    def test_readfile2memory(self):
        """测试analyzer.readfile2memory, 处理异常数据, 预期结果: 返回[]
        """
        filename = os.path.join(TMPPATH,"abc.gz")
        handle = gzip.open(filename, "w")
        handle.writelines(["%d\n" % i for i in range(10)])
        handle.close()
        total_lines,content = readfile2memory(filename)
        self.assertEqual(total_lines,10, "")
        self.assertEqual(len(content),10, "")
        
    def test_encode_message(self):
        """测试analyzer.encode_message, 处理异常数据, 预期结果: 返回[]
        """
        pass
    
    def test_process_content2kafka_valid(self):
        """测试analyzer.process_content2kafka, 处理正常数据, 预期结果: 
        """
        start,end,run_information = process_content2kafka(["abcde","b"],0,2,["a","b"],["topic1","topic2"])
        self.assertEqual(start, 0, "")
        self.assertEqual(end, 2, "")
        self.assertEqual(run_information.get("matchedlines",None), 2, "")
        self.assertNotEqual(run_information.get("start_timestamp",None), None, "")
        self.assertNotEqual(run_information.get("end_timestamp",None), None, "")
        self.assertEqual(run_information.get("errorinfo",None), [], "")

    def test_process_content2kafka_invalid(self):
        """测试analyzer.process_content2kafka, 处理异常数据, 预期结果: 
        """
        start,end,run_information = process_content2kafka(["abcde","b"],0,2,[r"(((a",r"b}}}"],["topic1","topic2"])
        self.assertEqual(start, 0, "")
        self.assertEqual(end, 2, "")
        self.assertEqual(run_information.get("matchedlines",None), 0, "")
        self.assertNotEqual(run_information.get("start_timestamp",None), None, "")
        self.assertNotEqual(run_information.get("end_timestamp",None), None, "")
        self.assertNotEqual(run_information.get("errorinfo",None), [], "")
    
    def test_get_execute_options_by_valid(self):
        """测试analyzer.get_execute_options_by, 处理正常数据, 预期结果: 
        """
        rules = [{u'status': u'active', u'parameters': u'{"topic": "haproxy_access_BeiJing_YiZhuang_CTC_log111_100_sso_funshion_com", "download_url": "http://traceall.funshion.com/_logcrawler/all_merged_gz/haproxy_access_BeiJing_YiZhuang_CTC_log111_100_sso_funshion_com/"}', u'timestamp': u'2013-06-26 17:49:05', u'IDC_ip_address_port': u'192.168.111.100:80', u'IDC_name': u'BeiJing_YiZhuang_CTC_log111_100', u'dealwith_manner': u'onserver', u'service_name': u'haproxy_access', u'regexp': u'sso.funshion.com', u'id': 10}, {u'status': u'active', u'parameters': u'{"topic": "haproxy__access__url-0", "kafka_url": "kafka://192.168.111.215:9092/"}', u'timestamp': u'2013-07-24 14:20:33', u'IDC_ip_address_port': u'0.0.0.0:0', u'IDC_name': u'all', u'dealwith_manner': u'sendtokafka', u'service_name': u'haproxy_access', u'regexp': u'jsonfe.funshion.com.*/.*', u'id': 688492}]
        self.assertEqual(get_execute_options_by(rules,"/a/haproxy_access/a.gz"), [u'all', u'haproxy_access', u'jsonfe.funshion.com.*/.*', u'sendtokafka', 'haproxy__access__url-0'], "")
        self.assertEqual(get_execute_options_by(rules,""), [], "")
        self.assertEqual(get_execute_options_by(rules,"/a/_haproxy_access/a.gz"), [], "")
        self.assertEqual(get_execute_options_by(rules,"/a/haproxy_access_/a.gz"), [], "")
    
    def test_get_execute_options_by_invalid(self):
        """测试analyzer.get_execute_options_by, 处理异常数据, 预期结果: 
        """
        rules = [{u'status': u'active', u'parameters': u'{"topic": "haproxy_access_BeiJing_YiZhuang_CTC_log111_100_sso_funshion_com", "download_url": "http://traceall.funshion.com/_logcrawler/all_merged_gz/haproxy_access_BeiJing_YiZhuang_CTC_log111_100_sso_funshion_com/"}', u'timestamp': u'2013-06-26 17:49:05', u'IDC_ip_address_port': u'192.168.111.100:80', u'IDC_name': u'BeiJing_YiZhuang_CTC_log111_100', u'dealwith_manner': u'onserver', u'service_name': u'haproxy_access', u'regexp': u'sso.funshion.com', u'id': 10}, {u'status': u'active', u'parameters': u'{"topic": "haproxy__access__url-0", "kafka_url": "kafka://192.168.111.215:9092/"}', u'timestamp': u'2013-07-24 14:20:33', u'IDC_ip_address_port': u'0.0.0.0:0', u'IDC_name': u'all', u'dealwith_manner': u'sendtokafka', u'service_name': u'haproxy_access', u'regexp': u'jsonfe.funshion.com.*/.*', u'id': 688492}]
        
        self.assertEqual(get_execute_options_by(rules,""), [], "")

if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(AnalyzerTestCases)
    unittest.TextTestRunner(verbosity=3).run(SUITE)
