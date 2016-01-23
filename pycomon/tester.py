import urllib.request as req
import datetime
import os
import re
from urllib.parse import urlparse
from subprocess import check_output, CalledProcessError
import threading

class Clock:
    def start(self):
        self.before = datetime.datetime.now()
    def stop(self):
        self.after =  datetime.datetime.now()

    def delta(self):
        dt = self.after - self.before
        micros = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds
        return micros

# purpose of this function is to perform a simple ping
def doping(host):
    if not host:
        return (False, 0)

    import os, platform
    if platform.system().lower() == "windows":
        try:
            o = check_output(["ping", "-n", "10", host]).decode("utf-8")
            res = re.findall(r"=(\d+)ms", o)
            return (True, sum(map(int, res)) / len(res))
        except CalledProcessError:
            return (False, 0)
    else:
        try:
            o = check_output(["ping", "-c", "10", host]).decode("utf-8")
            res = re.findall(r"time=(\d+)", o)
            return (True, sum(map(int, res)) / len(res))
        except CalledProcessError:
            return (False, 0)

# Purpose of this class is to perform tests and store results

class Result:
    def __init__(self, url, success, time, ping, size=0, duration=0):
        self.url = url
        self.time = time
        self.success = success
        # size in bytes
        self.size = size
        self.ping = ping
        # duratino in micros
        self.duration = duration
        self.speed = 0.0

    def result_line(self):
        self.recalculate()
        return [self.url, str(self.time), self.success, self.size, self.ping, self.duration, self.speed]

    def recalculate(self):
        if self.size < 0:
            self.size = 0

        if self.duration > 0:
            self.speed = (self.size * 1000000 / self.duration) / (1024 ** 2)
        else:
            self.speed = 0

    def __repr__(self):
        self.recalculate()
        return "Result(%s, %s, %s, %d, %f, %d, %f)" % \
               ( self.url
               , repr(self.time)
               , repr(self.success)
               , self.size
               , self.ping
               , self.duration 
               , self.speed )

class Test:
    def __init__(self, url):
        self.url = url
        self.progress = 0
        self.size = 0
        self.results = []
        self.enable = False

    def result_lines(self):
        return (r.result_line() for r in self.results)

    def ping_test(self):
        c = Clock()
        c.start()
        (success, ping) = doping(urlparse(self.url).hostname)
        return (success, ping, c.before)

    def dl_test(self):
        def report(blocknr, blocksize, size):
            self.progress = 10 + (90.0*(blocknr * blocksize)/size)
            self.size = size

        c = Clock()
        c.start()
        req.urlretrieve(self.url, reporthook=report)
        c.stop()

        return (self.size, c.delta(), c.before)

    def test(self):
        self.progress = 5.0
        (success, ping, time) = self.ping_test()
        res = Result(self.url, success, time, ping)
        self.progress = 10.0
        if success:
            (size, duration, time) = self.dl_test()
            res.size = size
            res.duration = duration
        self.progress = 100.0
        self.results.append(res)

class TestGroup:
    def __init__(self):
        self.running = False
        self.ordering = []
        self.test_dict = {}
        self.thread = None

    def reload(self, data):
        new_dict = {}
        self.ordering.clear()
        for url, p, e in data:
            self.ordering.add(url)

            if url in self.test_dict:
                new_dict[url] = self.test_dict[url]
            else:
                new_dict[url] = Test(url)

            new_dict[url].enable = e
        self.test_dict = new_dict

    def items(self):
        for url in self.ordering:
            p = self.test_dict[url].progress
            e = self.test_dict[url].enable
            yield url, p, e


    def start(self):
        def run_tests():
            for t in self.test_dict.values():
                if t.enabled:
                    t.test()
            self.thread = None

        if self.thread:
            return
        else:
            self.thread = threading.Thread(target=run_tests())

    def kill(self):
        if self.thread:
            self.thread.join(0.0)
