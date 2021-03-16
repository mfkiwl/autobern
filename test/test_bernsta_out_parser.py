#! /usr/bin/python
#-*- coding: utf-8 -*-

from __future__ import print_function
import sys
import os
import re
import argparse
import datetime
from shutil import copyfileobj
import pybern.products.bernparsers.bern_out_parse as bparse

if len(sys.argv) != 2:
    print('[ERROR] Need to provide a .OUT file')
    sys.exit(1)

bout = sys.argv[1]
with open(bout, 'r') as f:
    dct = bparse.parse_generic_out_header(f)
print(dct)