#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core import TestBench
import argparse
import sys

parser = argparse.ArgumentParser(description='''verilogのテストベンチファイルを自動生成するスクリプトです
https://github.com/cagayakemiracl/verilog_test_bench_auto
''')
parser.add_argument('file_list', nargs='*', help='コンパイル時に渡すファイル')
parser.add_argument('-s', '--topmodule', nargs='?', default='', help='テストベンチを生成したいモジュール')
parser.add_argument('-i', '--input', nargs='?', default='', help='テストベンチを生成したいモジュールを含むファイル')
parser.add_argument('-o', '--output', nargs='?', default='', help='テストベンチファイル名又はディレクトリ')
parser.add_argument('-p', '--path', nargs='?', default='', help='iverilogなどのツールがあるディレクトリ')
parser.add_argument('-f', '--found', nargs='?', default='', help='指定したモジュールが含まれるファイルを検索')
parser.add_argument('-r', '--run', action='store_true', help='コンパイルして実行')
parser.add_argument('-w', '--wave', action='store_true', help='GtkWaveを使って波形の表示')
parser.add_argument('-c', '--clean', action='store_true', help='生成したテストベンチを削除')
parser.add_argument('-v', '--version', action='version', version='test_bench 0.3')
args = parser.parse_args()

if args.found:
    print ('%sは%sの中にあります' % (args.found, TestBench.found_module(args.found, args.file_list)))
    sys.exit(0)

test_bench = TestBench(args.file_list, args.input, args.output, args.topmodule, args.path)
if args.run:
    test_bench.run()

if args.wave:
    test_bench.show_wave()

if args.clean:
    test_bench.clean()
