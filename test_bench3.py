#!/usr/bin/env python3
from test_bench_core3 import Test_bench
from sys import argv

argv.pop(0)
Test_bench(argv).run()
