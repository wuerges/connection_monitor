import urllib.request as req
import datetime
import os
import re
from urllib.parse import urlparse
from subprocess import check_output

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
  import os, platform
  if platform.system().lower() == "windows":
    raise "Not implemented for windows"
    # r = os.system("ping -n 10 " + host)
  else:
    try:
      o = check_output(["ping", "-c", "10", host]).decode("utf-8")
      res = re.findall(r"time=(\d+)", o)
      return (True, sum(map(int, res)) / len(res))
    except CalledProcessError:
      return (False, 0)

# Purpose of this class is to perform tests and store results

class Result:
  def __init__(self, success, time, ping, size=0, duration=0):
    self.time = time
    self.success = success
    self.size = size
    self.ping = ping
    self.duration = duration
    self.speed = 0

  def recalculate(self):
    self.speed = (self.size * 1000000 / self.duration)

  def __repr__(self):
    self.recalculate()
    return "Result(%s, %s, %d, %f, %d, %d)" % \
             ( repr(self.time)
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

  def ping_test(self):
    c = Clock()
    c.start()
    (success, ping) = doping(urlparse(self.url).hostname)
    return (success, ping, c.before)

  def dl_test(self):
    def report(blocknr, blocksize, size):
      self.progress = 100.0*(blocknr * blocksize)/size
      self.size = size
      print(self.progress)

    self.progress = 0
    c = Clock()
    c.start()
    req.urlretrieve(self.url, reporthook=report)
    c.stop()

    return (self.size, c.delta(), c.before)

  def test(self):
    (success, ping, time) = self.ping_test()
    res = Result(success, time, ping)
    if success:
      (size, duration, time) = self.dl_test()
      res.size = size
      res.duration = duration
    self.results.append(res)


if True:
  # t = Test("http://www.python.org/")
  t = Test("http://ipv4.download.thinkbroadband.com/20MB.zip")
  t.test()
  print(t.results)
