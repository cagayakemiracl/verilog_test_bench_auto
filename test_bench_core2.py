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

def print_type(line):
    line = line.strip()
    type = get_type(line)
    print "type is %s '%s'" % (type, line)
    return line.replace(type, "").strip()

def add_str(list):
    return reduce(lambda x, y: x + y, list);

def port2obj(line):
    dic = {
    "input" : "reg  ",
    "output" : "wire "
    }
    port = get_type(line)
    port_rm = line.replace(port, "").strip()
    return dic.get(port, "") + port_rm

class Test_bench:
    def __init__(self, file_name):
        self.sorce_file = file_name;
        self.base, ext = os.path.splitext(self.sorce_file)
        self.dest_file = self.base + "_test.v"
        self.dump_file = self.base + ".vcd"
        self.bit_sum = 1
        self.argl = []
        self.inputl = []
        self.objl = []
        self.clk = False

        self.analysis()
        self.output_file()

    def analysis(self):
        target = False
        with open(self.sorce_file, 'r') as f:
            for line in f:
                if "input" in line and target:
                    bit_num = 0
                    attr = self.spl_val(line)
                    if re.match("^\[", attr[0]):
                        bit_list = map(int, my_split("\[|:|\]", attr[0]))
                        bit_num = 2 ** (int(math.fabs(bit_list[0] - bit_list[1])) + 1)
                        attr.pop(0)
                    else:
                        bit_num = 2

                    self.argl += attr
                    if "clk" in attr:
                        self.clk = True
                        attr.pop(attr.index("clk"))

                    self.bit_sum *= bit_num ** len(attr)
                    self.inputl += attr
                    print attr
                    print bit_num
                    print self.bit_sum
                elif "output" in line and target:
                    attr = self.spl_val(line)
                    if re.match("^\[", attr[0]):
                        attr.pop(0)

                    self.argl += attr
                elif "endmodule" in line and target:
                    print_type(line)
                    break
                elif "module" in line:
                    line = print_type(line)
                    tmp = my_split("\s", line)
                    name = tmp[0]
                    print name
                    if self.base == name:
                        target = True

                else:
                    print_type(line)

        self.args = list2str(self.argl)
        self.inputs = list2str(self.inputl)
        print self.args
        print self.inputs

    def output_file(self):
        with open(self.dest_file, 'w') as f:
            f.write("""/*
\tThis program has been automatically generated by the following script.
\thttps://github.com/cagayakemiracl/verilog_test_bench_auto
\tThank you!!
*/
module test_bench ();
%s""" % add_str(map(lambda x: "\t%s\n" % x, self.objl)))
            if self.clk:
                f.write("\talways #5 clk <= !clk;\n\tinitial clk = 0;")

            f.write('''
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
''' % (self.base,
       list2str(map(lambda x: ".%s(%s)" % (x, x), self.argl)),
       self.dump_file,
       add_str(map(lambda x: " %s = %%b" % x, self.argl)),
       self.args,
       add_str(map(lambda x: "\t\t%s = 0;\n" % x, self.inputl)),
       self.bit_sum,
       self.inputs,
       self.inputs,
       self.bit_sum))

    def compile_file(self):
        os.system("iverilog %s %s" % (self.sorce_file, self.dest_file))

    def exec_file(self):
        os.system("vvp a.out")

    def rm_aout(self):
        os.system("rm a.out")

    def run(self):
        self.compile_file()
        self.exec_file()
        self.rm_aout()

    def obj_append(self, line):
        self.objl.append(port2obj(line))

    def spl_val(self, line):
        self.obj_append(line)
        tmp = print_type(line)
        return my_split(",|;|\s", tmp)
