#!/usr/bin/env python2.7
from test_bench_core2 import Test_bench
from sys import argv

argv.pop(0)
Test_bench(argv).run()
