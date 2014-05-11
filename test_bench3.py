#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from test_bench_core3 import Test_bench
import argparse

parser = argparse.ArgumentParser(description='''verilogのテストベンチファイルを自動生成するスクリプトです
https://github.com/cagayakemiracl/verilog_test_bench_auto
''')
parser.add_argument('file_list', nargs='*', help='コンパイル時に渡すファイル')
parser.add_argument('-s', '--topmodule', nargs='?', default='', help='テストベンチを生成したいモジュール')
parser.add_argument('-i', '--input', nargs='?', default='', help='テストベンチを生成したいモジュールを含むファイル')
parser.add_argument('-o', '--output', nargs='?', default='', help='テストベンチファイル名')
parser.add_argument('-v', '--version', action='version', version='test_bench 0.1')
args = parser.parse_args()

Test_bench(args.file_list, args.input, args.output, args.topmodule).run()
