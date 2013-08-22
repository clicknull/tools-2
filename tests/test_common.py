#!/usr/bin/env python
# coding: utf-8


import os
import shutil
import logging
import unittest
from logcrawler import common


logging.disable(logging.CRITICAL)

TMPPATH = "tmp"

class CommonTestCases(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(TMPPATH):
            os.makedirs(TMPPATH)

    def tearDown(self):
        shutil.rmtree(TMPPATH)

    def test_makedirs1(self):
        """测试common.makedirs(), path合法，且路径中有不存在的文件夹，预期结果: 返回True
        """
        self.assertEqual(common.makedirs(os.path.join(TMPPATH, "level1", "level2")),
            True, 'create multiple level sub directories passed')
        self.assertEqual(
            os.path.exists(os.path.join(TMPPATH, "level1", "level2")),
            True, 'sub level sub directories passed')
        self.assertEqual(
            os.path.exists(os.path.join(TMPPATH, "level1")),
            True, 'first level sub directories passed')

    def test_makedirs2(self):
        """测试common.makedirs(), path合法，且path指定的目录已经存在，预期结果: 返回True
        """
        os.mkdir(os.path.join(TMPPATH, "level1"))
        os.mkdir(os.path.join(TMPPATH, "level1", "level2"))
        self.assertEqual(
            common.makedirs(os.path.join(TMPPATH, "level1", "level2")),
            True, 'create multiple level sub directories passed')

    def test_makedirs3(self):
        """测试common.makedirs(), path合法，且路径中有存在的文件，预期结果: 返回False
        """
        os.mkdir(os.path.join(TMPPATH, "level1"))
        file_object = open(os.path.join(TMPPATH, "level1", "makedirs3.txt"), "w")
        file_object.write("str")
        file_object.close()

        self.assertEqual(
            common.makedirs(os.path.join(TMPPATH, "level1", "makedirs3.txt", "level2")),
            False, 'create multiple level sub directories failed')

    # def test_RestWrapper_get(self):
    #     """测试common.RestWrapper的get方法
    #     """
    #     restWrapper = common.RestWrapper()
    #     json_content = restWrapper.get("url")
    #     self.assertEqual(len(json_content), 0, '')

    # def test_RestWrapper_post(self):
    #     """测试common.RestWrapper的post方法
    #     """
    #     restWrapper = common.RestWrapper()
    #     json_content = restWrapper.post("url")
    #     self.assertEqual(len(json_content), 0, '')
    #     json_content = restWrapper.post("url",data="",timeout=2)
    #     self.assertEqual(len(json_content), 0, '')


if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(CommonTestCases)
    unittest.TextTestRunner(verbosity=3).run(SUITE)
