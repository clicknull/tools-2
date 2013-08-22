#!/usr/bin/env python
#coding: UTF-8

""" Unit test for factory
"""

import unittest
import logging

from logcrawler import factory

logging.disable(logging.CRITICAL)


class FactoryTestCases(unittest.TestCase):

    def setUp(self):
        self.taskFactory = factory.TaskFactory()

    def tearDown(self):
        self.taskFactory = None

    def test_get_tasks_normal_default(self):
        """TEST: factory.TaskFactory().get_tasks(), IN: None, set _flag normal, OUT: task list"""
        pass

    def test_get_tasks_too_early_default(self):
        """TEST: factory.TaskFactory().get_tasks(), IN: None, set _flag late, OUT: empty list"""
        pass

    def test_get_tasks_normal(self):
        """TEST: factory.TaskFactory().get_tasks(), IN: normal timestamp, OUT: task list"""
        pass

    def test_get_tasks_too_early(self):
        """TEST: factory.TaskFactory().get_tasks(), IN: early timestamp, OUT: empty list"""
        pass

    def test_get_tasks_wtih_empty_settings(self):
        """TEST: factory.TaskFactory().get_tasks(), IN: set _settings empty, OUT: empty list"""
        pass

    def test_get_tasks_times_normal(self):
        """TEST: factory.TaskFactory().get_tasks_times(), IN: normal timestamp, OUT: time list"""
        pass

    def test_get_tasks_times_too_early(self):
        """TEST: factory.TaskFactory().get_tasks_times(), IN: early timestamp, OUT: empty list"""
        pass

    def test_create_task_normal(self):
        """TEST: factory.TaskFactory().create_task(), IN: normal params, OUT: a correct task"""
        pass

    def test_create_task_configs_illegal(self):
        """TEST: factory.TaskFactory().create_task(), IN: configs illegal, OUT: empty task"""
        pass

    def test_create_task_sampling_skip(self):
        """TEST: factory.TaskFactory().create_task(), IN: config sampling skip, OUT: empty task"""
        pass

    def test_illegal_config_legal(self):
        """TEST: factory.TaskFactory()._illegal(), IN: legal configs, OUT: False"""
        pass

    def test_illegal_config_illegal(self):
        """TEST: factory.TaskFactory()._illegal(), IN: illegal configs, OUT: True"""
        pass

    def test_hit_sampling_hit(self):
        """TEST: factory.TaskFactory()._hit_sampling(), IN: sampling hit, OUT: True"""
        pass

    def test_hit_sampling_skip(self):
        """TEST: factory.TaskFactory()._hit_sampling(), IN: sampling skip, OUT: False"""
        pass


if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(FactoryTestCases)
    unittest.TextTestRunner(verbosity=3).run(SUITE)
