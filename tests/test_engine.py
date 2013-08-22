#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Unit test for engine module
"""

import Queue
import unittest
import threading
import logging
import time

from logcrawler.engine import Engine


logging.disable(logging.CRITICAL)


class EngineTestCases(unittest.TestCase):
    def setUp(self):
        tc = TaskCreator()
        self.engine = Engine(tc, 5)

    def tearDown(self):
        # self.engine.terminate()
        pass

    def test_start_scheduler(self):
        self.engine.start_scheduler()
        time.sleep(10)
        self.engine.stop_scheduler()
        qsize = self.engine._task_queue.qsize()
        self.assertTrue(qsize > 0)

    def test_start_checker(self):
        self.engine.start_checker()
        self.assertTrue(self.engine.checker.is_alive())
        self.engine.stop_checker()

    def test_stop_checker(self):
        self.engine.start_checker()
        self.assertTrue(self.engine.checker.is_alive())
        self.engine.stop_checker()
        time.sleep(1)
        self.assertFalse(self.engine.checker.is_alive())

    def test_get_task(self):
        self.engine._task_queue.put("a")
        self.engine._task_queue.put({"foo": "bar"})
        task = self.engine.get_task()
        self.assertEqual(task, "a")
        task = self.engine.get_task()
        self.assertEqual(task, {"foo": "bar"})

        task = self.engine.get_task(block=True, timeout=5)
        self.assertEqual(task, {})

    def test_put_task(self):
        self.engine.put_task({"foo": "bar"})
        self.assertEqual(self.engine.get_task(), {"foo": "bar"})

        self.engine.put_task({})
        self.assertEqual(self.engine.get_task(), {})

    def test_put_task_with_delay(self):
        self.engine.put_task({'foo': 'bar'}, 5)
        self.assertEqual(self.engine.get_task(block=True, timeout=1), {})
        self.assertEqual(self.engine.get_task(block=True, timeout=10), {"foo": "bar"})

    def test_get_result(self):
        async_result = AsyncResult("aaa", "SUCCESS")
        self.engine._result_queue.put(async_result)
        self.assertEqual(self.engine.get_result(), async_result)

    def test_get_result_with_timeout(self):
        self.assertEqual(self.engine.get_result(block=False), None)

    def test_put_result(self):
        async_result = AsyncResult("aaa", "SUCCESS")
        self.engine.put_result(async_result)
        self.assertEqual(self.engine._result_queue.get(), async_result)

    def test_check_with_httperr(self):
        result = {'url': 'www.funshion.com', 'result': 'httperr', 'local_path': ''}
        async_result = AsyncResult(result, 'SUCCESS')
        deadline = time.time() + 60 * 5

        self.engine.put_result((async_result, deadline))
        self.engine.start_checker()
        time.sleep(2)
        self.engine.stop_checker()
        time.sleep(2)

        # test task retry
        expect_task = {'url': 'www.funshion.com', 'deadline': deadline}
        self.assertEqual(self.engine.get_task(), expect_task)

    def test_check_with_ioerr(self):
        result = {'url': 'www.funshion.com', 'result': 'ioerr', 'local_path': ''}
        async_result = AsyncResult(result, 'SUCCESS')
        deadline = time.time()

        self.engine.put_result((async_result, deadline))
        self.engine.start_checker()
        time.sleep(2)
        self.engine.stop_checker()
        time.sleep(2)
        # test result is alread digest
        while self.engine._result_queue.qsize():
            self.assertNotEqual(self.engine.get_result(), (result, deadline))

    def test_schedule(self):
        self.engine.schedule()
        self.assertEqual(self.engine._task_queue.qsize(), 5)

    def test_run(self):
        pass

class AsyncResult:
    def __init__(self, result, state):
        self.result = result
        self.state = state
        
    def get(self):
        return self.result

class TaskCreator(object):
    def get_tasks(self):
        tasks = []
        for i in range(5):
            # set deadline to 60s
            task = {"src": "www.funshion.com", "deadline": time.time() + 60}
            tasks.append(task)
        return tasks

    def start(self):
        pass

    def stop(self):
        pass

if __name__ == "__main__":
    unittest.main()
