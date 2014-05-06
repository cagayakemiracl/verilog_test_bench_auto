import os.path
import os
import re
import math
from functools import reduce
            
class Test_bench:
    def __init__(self, file_name):
        self.sorce_file = file_name;
        base, ext = os.path.splitext(self.sorce_file)
        self.dest_file = base + "_test.v"
        self.dump_file = base + ".vcd"
        self.bit_sum = 1
        self.argl = []
        self.inputl = []
        self.analysis()
        self.output_file()

    def split(self, match, string):
        tmp = re.split(match, string)
        while(True):
            try:
                tmp.remove("")
            except ValueError:
                break

        return tmp

    def list2str(self, list):
        return reduce(lambda x, y: x + ", " + y, list)
        
    def analysis(self):
        with open(self.dest_file, 'w') as f:
            f.write("module test_bench();\n")
            for line in open(self.sorce_file, 'r'):
                if "input" in line:
                    bit_num = 0
                    print("type is input %s" % line, end=' ')
                    line = line.replace("input", "").strip()
                    f.write("\treg  %s\n" % line)
                    attr = self.split(",|;|\s", line)
                    if re.match("^\[", attr[0]):
                        bit_list = list(map(int, self.split("\[|:|\]", attr[0])))
                        bit_num = 2 ** (int(math.fabs(bit_list[0] - bit_list[1])) + 1)
                        attr.pop(0)
                    else:
                        bit_num = 2

                    self.bit_sum *= bit_num ** len(attr)
                    self.argl += attr
                    self.inputl += attr 
                    print(attr)
                    print(bit_num)
                    print(self.bit_sum)
                elif "output" in line:
                    print("type if output %s" % line, end=' ')
                    line = line.replace("output", "").strip()
                    f.write("\twire %s\n" % line)
                    attr = self.split(",|;|\s", line)
                    if re.match("^\[", attr[0]):
                        attr.pop(0)

                    self.argl += attr
                elif "module" in line and "endmodule" not in line:
                    print("type is module %s" % line, end=' ')
                    tmp = self.split("\s", line)
                    self.name = tmp[1]
                    print(self.name)
                else:
                    print("bat strings %s" % line, end=' ')

        self.args = self.list2str(self.argl)
        self.inputs = self.list2str(self.inputl)
        print(self.args)
        print(self.inputs)

    def output_file(self):
        with open(self.dest_file, 'a') as f:
            f.write('''
\t%s i0 (%s);

\tinitial begin
\t\t$dumpfile("%s");
\t\t$dumpvars(0, test_bench);
\t\t$monitor("%%t''' % (self.name, self.args, self.dump_file))
            for attr in self.argl:
                f.write(" %s = %%b" % attr)

            f.write('", $time, %s);\n' % self.args)
            for attr in self.inputl:
                f.write("\t\t%s = 0;\n" % attr)

            f.write("""
\t\trepeat (%d) begin
\t\t\t#10;
\t\t\t{%s} = {%s} + 1;
\t\tend // repeat (%d) begin
\t\t$finish;
\tend // initial begin
endmodule // test_bench
""" % (self.bit_sum, self.inputs, self.inputs, self.bit_sum))

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
