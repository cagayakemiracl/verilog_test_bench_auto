with open('test_bench_core3.py', 'w') as f:
    for line in open('tmp.py', 'r'):
        if "end=' '" in line:
            line = line.replace("end=' '", "end=''")

        f.write(line)
