import os.path
import os
import re
import math

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
    return add_list(map(lambda x: x.pop(1), list))

def exec_file():
    os.system("vvp a.out")

def rm_aout():
    os.system("rm a.out")

class Test_bench:
    def __init__(self, file_list, input, output, topmodule):
        self.file_list = file_list
        if input:
            self.source_file = input
            self.file_list.append(input)
        else:
            self.source_file = file_list[0]

        if topmodule:
            self.module = topmodule
        else:
            basename = os.path.basename(self.source_file)
            self.module, ext = os.path.splitext(basename)

        if output:
            base, ext = os.path.splitext(output)
            if ext:
                self.dest_file = output
                self.dump_file = base + '.vcd'
            else:
                join = os.path.join(output, self.module)
                self.dest_file = join + '.v'
                self.dump_file = join + '.vcd'

        else:
            self.base, ext = os.path.splitext(self.source_file)
            self.dest_file = self.base + "_test.v"
            self.dump_file = self.base + ".vcd"

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
                    attr, bit_num = self.spl_val(line)
                    self.bit_sum *= bit_num ** len(attr)
                    self.inputl.append([bit_num, attr])
                elif "output" in line and target:
                    attr, bit_num = self.spl_val(line)
                    self.outputl.append([bit_num, attr])
                elif "endmodule" in line and target:
                    break
                elif "module" in line:
                    line = rm_type(line)
                    tmp = my_split("\s|\(", line)
                    name = tmp[0]
                    if self.module == name:
                        target = True

        self.inputl = sort_bit(self.inputl)
        self.outputl = sort_bit(self.outputl)
        self.argl = self.outputl + self.inputl
        self.args = list2str(self.argl)
        if "clk" in self.inputl:
            self.clk = "\n\talways #5 clk <= !clk;\n\tinitial clk = 0;\n"
            self.inputl.pop(self.inputl.index("clk"))

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
''' % (add_list(map(lambda x: "\t%s\n" % x, self.objl)),
       self.clk,
       self.module,
       list2str(map(lambda x: ".%s(%s)" % (x, x), self.argl)),
       self.dump_file,
       add_list(map(lambda x: " %s = %%b" % x, self.argl)),
       self.args,
       add_list(map(lambda x: "\t\t%s = 0;\n" % x, self.inputl)),
       self.bit_sum,
       self.inputs,
       self.inputs,
       self.bit_sum))

    def compile_file(self):
        os.system("iverilog -s test_bench %s%s" % (self.dest_file, add_list(map(lambda x: " %s" % x, self.file_list))))

    def run(self):
        self.compile_file()
        exec_file()
        rm_aout()

    def spl_val(self, line):
        self.objl.append(port2obj(line))
        tmp = rm_type(line)
        attr = my_split(",|;|\s", tmp)
        if re.match("^\[", attr[0]):
            bit_list = map(int, my_split("\[|:|\]", attr[0]))
            bit_num = 2 ** (int(math.fabs(bit_list[0] - bit_list[1])) + 1)
            attr.pop(0)
        else:
            bit_num = 2

        return attr, bit_num
