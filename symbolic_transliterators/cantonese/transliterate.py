#!/usr/bin/env python
from __future__ import print_function
import argparse
import mapping


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='input filepath', required=True)
    parser.add_argument('--output', '-o', help='output filepath', required=True)
    args = parser.parse_args()

    words = [l.strip() for l in open(args.input)]

    with open(args.output, 'w') as fg:
        for entry in mapping.mapping(words):
            print(' . '.join([syl.placeTone().toString() for syl in entry]), file=fg)
