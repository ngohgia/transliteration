#!/usr/bin/python


def load_dict(file_name):
    ret = {}
    with open(file_name) as fh:
        for line in fh.readlines():
            if len(line) == 0 or line[0] == '#':
                continue
            symbols = line.strip().split(',')
            for idx in range(1, len(symbols)):
                ret[symbols[idx]] = symbols[0]
    return ret
