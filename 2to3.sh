#!/bin/sh
cp test_bench_core2.py tmp.py
2to3 -w tmp.py
python3 2to3.py
rm -rf __pycache__ tmp.py tmp.py.bak
