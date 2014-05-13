import os.path
import os
import re
import filecmp
import sys
from functools import reduce

def my_split(match, string):
    tmp = re.split(match, string)
    while(True):
        try:
            tmp.remove("")
        except ValueError:
            break

    return tmp

def list2str(list):
    return reduce(lambda x, y: x + ", " + y, list)

def get_type(line):
    line_spl = my_split("\s", line)
    try:
        ret = line_spl[0]
    except IndexError:
        ret = ""

    return ret

def rm_type(line):
    line = line.strip()
    type = get_type(line)
    return line.replace(type, "").strip()

def add_list(list):
    return reduce(lambda x, y: x + y, list);

def port2obj(line):
    dic = {
    "input" : "reg  ",
    "output" : "wire "
    }
    port = get_type(line)
    port_rm = line.replace(port, "").strip()
    return dic.get(port, "") + port_rm

def sort_bit(list):
    list.sort()
    list.reverse()
    return add_list([x.pop(1) for x in list])

def is_eq_module(line, name):
    if "module" in line:
        line = rm_type(line)
        tmp = my_split("\s|\(", line)
        if tmp[0] == name:
            return True

    return False

def my_remove(file):
    if os.path.exists(file):
        os.remove(file)

def rm_aout():
    my_remove("a.out")

def print_error(string):
    print(string)
    sys.exit(1)

def check_veri(string):
    base, ext = os.path.splitext(string)
    if ext != '.v':
        print_error("指定したファイルがverilogファイルではありません! %s" % string)

    return string

def not_found_module(module):
    print_error ("指定したモジュールが見つかりませんでした! %s" % module)

def cat_file(file):
    with open(file, 'r') as f:
        print(f.read())

class TestBench:
    @classmethod
    def found_module(self, module, file_list):
        for file in file_list:
            if not os.path.exists(file):
                print_error("ファイルが存在しません! %s" % file)

            check_veri(file)
            with open(file, 'r') as f:
                for line in f:
                    if is_eq_module(line, module):
                        return file

        not_found_module(module)

    def __init__(self, file_list, input='', output='', topmodule='', path=''):
        for file in file_list:
            check_veri(file)

        self.file_list = file_list
        if input:
            self.source_file = check_veri(input)
            if input not in file_list:
                self.file_list.append(input)
        else:
            try:
                self.source_file = file_list[0]
            except IndexError:
                print_error("入力ファイルを渡してください!")

        if topmodule:
            self.module = topmodule
            if not input:
                self.source_file = self.found_module(self.module, file_list)

        else:
            basename = os.path.basename(self.source_file)
            self.module, ext = os.path.splitext(basename)

        if output:
            base, ext = os.path.splitext(output)
            if ext:
                self.dest_file = check_veri(output)
                self.dump_file = base + '.vcd'
            else:
                if not os.path.isdir(output):
                    os.makedirs(output)

                join = os.path.join(output, self.module + "_test")
                self.dest_file = join + '.v'
                self.dump_file = join + '.vcd'

        else:
            base, ext = os.path.splitext(self.source_file)
            base += '_test'
            self.dest_file = base + ".v"
            self.dump_file = base + ".vcd"

        for file in self.file_list:
            if os.path.exists(self.dest_file) and filecmp.cmp(file, self.dest_file):
                print_error("入力ファイルと出力ファイルが同じです! %s" % file)

        self.iverilog = os.path.join(path, "iverilog")
        self.vvp = os.path.join(path, "vvp")
        self.gtk_wave = os.path.join(path, "gtkwave")
        self.bit_sum = 1
        self.argl = []
        self.inputl = []
        self.outputl = []
        self.objl = []
        self.clk = ""
        self.analysis()
        self.output_file()

    def analysis(self):
        target = False
        with open(self.source_file, 'r') as f:
            for line in f:
                if "input" in line and target:
                    attr, bit_num = self._spl_val(line)
                    self.bit_sum *= bit_num ** len(attr)
                    self.inputl.append([bit_num, attr])
                elif "output" in line and target:
                    attr, bit_num = self._spl_val(line)
                    self.outputl.append([bit_num, attr])
                elif "endmodule" in line and target:
                    break
                elif not target:
                    target = is_eq_module(line, self.module)

        if not target:
            not_found_module(self.module)

        if not len(self.inputl):
            print_error("入力ポートが見当たりません!")

        if not len(self.outputl):
            print_error("出力ポートが見当たりません!")

        self.inputl = sort_bit(self.inputl)
        self.outputl = sort_bit(self.outputl)
        self.argl = self.outputl + self.inputl
        self.args = list2str(self.argl)
        if "clk" in self.inputl:
            self.clk = "\n\talways #5 clk <= !clk;\n\tinitial clk = 0;\n"
            self.inputl.pop(self.inputl.index("clk"))
            self.bit_sum /= 2

        self.inputs = list2str(self.inputl)

    def output_file(self):
        with open(self.dest_file, 'w') as f:
            f.write('''/*
\tThis program has been automatically generated by the following script.
\thttps://github.com/cagayakemiracl/verilog_test_bench_auto
\tThank you!!
*/
module test_bench ();
%s%s
\t%s i0 (%s);

\tinitial begin
\t\t$dumpfile ("%s");
\t\t$dumpvars (0, test_bench);
\t\t$monitor  ("%%t%s", $time, %s);
%s
\t\trepeat (%d) begin
\t\t\t#10;
\t\t\t{%s} = {%s} + 1;
\t\tend // repeat (%d) begin
\t\t$finish;
\tend // initial begin
endmodule // test_bench
''' % (add_list(["\t%s\n" % x for x in self.objl]),
       self.clk,
       self.module,
       list2str([".%s(%s)" % (x, x) for x in self.argl]),
       self.dump_file,
       add_list([" %s = %%b" % x for x in self.argl]),
       self.args,
       add_list(["\t\t%s = 0;\n" % x for x in self.inputl]),
       self.bit_sum,
       self.inputs,
       self.inputs,
       self.bit_sum))

    def compile_file(self):
        os.system("%s -s test_bench %s%s" % (self.iverilog,
                                             self.dest_file,
                                             add_list([" %s" % x for x in self.file_list])))

    def exec_file(self):
        if not os.path.exists("a.out"):
            self.compile_file()

        os.system("%s a.out" % self.vvp)

    def show_wave(self):
        if not os.path.exists(self.dump_file):
            self.exec_file()

        os.system("%s %s" % (self.gtk_wave, self.dump_file))
        rm_aout()

    def run(self):
        self.exec_file()
        rm_aout()

    def clean(self):
        rm_aout()
        my_remove(self.dest_file)
        my_remove(self.dump_file)

    def cat_test(self):
        cat_file(self.source_file)
        cat_file(self.dest_file)

    def _spl_val(self, line):
        self.objl.append(port2obj(line))
        tmp = rm_type(line)
        attr = my_split(",|;|\s", tmp)
        if re.match("^\[", attr[0]):
            bit_list =  [int(x) for x in my_split("\[|:|\]", attr[0])]
            bit_num = 2 ** (abs(bit_list[0] - bit_list[1]) + 1)
            attr.pop(0)
        else:
            bit_num = 2

        return attr, bit_num
