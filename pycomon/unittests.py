from tester import *

import csv

c = Clock()
c.start()
c.stop()

t = Test("http://www.google.com")

t.test()


with open('some.csv', 'w') as f:
    w = csv.writer(f)
    w.writerows(t.result_lines())
