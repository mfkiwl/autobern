#! /usr/bin/python3
#-*- coding: utf-8 -*-

from __future__ import print_function
import sys
import argparse
import datetime
from pybern.products.codedcb import get_dcb, list_products
from pybern.products.formats.sp3 import Sp3
import pybern.products.fileutils.decompress as dc
import pybern.products.fileutils.compress as cc
from pybern.products.fileutils.cmpvar import is_compressed, find_os_compression_type
import time
##  If only the formatter_class could be:
##+ argparse.RawTextHelpFormatter|ArgumentDefaultsHelpFormatter ....
##  Seems to work with multiple inheritance!
class myFormatter(argparse.ArgumentDefaultsHelpFormatter,
                  argparse.RawTextHelpFormatter):
    pass


parser = argparse.ArgumentParser(
    formatter_class=myFormatter,
    description=
    'Download Differential Code Bias (DCB) files estimated at CODE ac',
    epilog=('''National Technical University of Athens,
    Dionysos Satellite Observatory\n
    Send bug reports to:
    Xanthos Papanikolaou, xanthos@mail.ntua.gr
    Dimitris Anastasiou,danast@mail.ntua.gr
    January, 2021'''))

parser.add_argument('-y',
                    '--year',
                    metavar='YEAR',
                    dest='year',
                    type=int,
                    required=False,
                    help='The year of date.')

parser.add_argument('-d',
                    '--doy',
                    metavar='DOY',
                    dest='doy',
                    type=int,
                    required=False,
                    help='The day-of-year (doy) of date.')

parser.add_argument(
    '-o',
    '--output',
    metavar='OUTPUT',
    dest='save_as',
    required=False,
    help='Save the downloaded file using this file(name); can include path.')

parser.add_argument(
    '-O',
    '--output-dir',
    metavar='OUTPUT_DIR',
    dest='save_dir',
    required=False,
    help='Save the downloaded file under the given directory name.')

parser.add_argument(
    '-t',
    '--type',
    choices=['final', 'rapid', 'current'],
    metavar='TYPE',
    dest='type',
    required=False,
    help=
    'Choose type of solution; can be any of \"final, rapid, current\". Can be ommited if CODE_TYPE unambiguously defines a DCB file.'
)

parser.add_argument('-s',
                    '--time-span',
                    metavar='TIME_SPAN',
                    dest='span',
                    required=False,
                    choices=['daily', 'monthly'],
                    default='monthly',
                    help='Choose between daily of monthly DCB files.')

parser.add_argument('-c',
                    '--code-type',
                    metavar='CODE_TYPE',
                    dest='obs',
                    required=False,
                    default='p1c1',
                    help='Choose the code type(s) that the DCB file includes')
parser.add_argument('--verbose',
                    dest='verbose',
                    action='store_true',
                    help='Trigger verbose run (prints debug messages).')

parser.add_argument('-l',
                    '--list-products',
                    dest='list_products',
                    action='store_true',
                    help='List available DCB products and exit')

if __name__ == '__main__':

    args = parser.parse_args()
    
    ## verbose print
    verboseprint = print if args.verbose else lambda *a, **k: None

    ## if we are just listing products, print them and exit.
    if args.list_products:
        list_products()
        sys.exit(0)
    
    ## if we have a year or a doy then both args must be there!
    if (args.year is not None and args.doy is None) or (args.doy is not None and args.year is None):
        print('[ERROR] Need to specify both Year and DayOfYear', file=sys.stderr)
        sys.exit(1)

    ## store user options in a dictionary to pass to the download function.
    input_dct = {'span': args.span, 'obs': args.obs}
    if args.year:
        input_dct['pydt'] = datetime.datetime.strptime(
            '{:4d}-{:03d}'.format(args.year, args.doy), '%Y-%j')
    if args.type is not None:
        input_dct['type'] = args.type
    if args.save_as:
        input_dct['save_as'] = args.save_as
    if args.save_dir:
        input_dct['save_dir'] = args.save_dir

#    ## try downloading the dcb file; if we fail do not throw, print the error
#    ## message and return an intger > 0 to the shell.
#    status = 10
#    try:
#        status, remote, local = get_dcb(**input_dct)
#    except Exception as e:
#        verboseprint("{:}".format(str(e)), file=sys.stderr)
#        status = 50
#    if not status:
#        print('Downloaded DCB Information File: {:} as {:}'.format(
#            remote, local))
#        sys.exit(0)
#    else:
#        print('[ERROR] Failed to download DCB product', file=sys.stderr)
#
#    sys.exit(status)

    ## ---- Change the function above to try 10 times for DCB file
    ## Maximum retries and sleep duration in seconds
    MAX_RETRIES = 10
    SLEEP_DURATION = 300

    def verboseprint(*args, **kwargs):
        print(*args, **kwargs)

    status = 10  # Default status indicating failure
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            verboseprint(f"Attempt {attempt}/{MAX_RETRIES} to download DCB product.")
            status, remote, local = get_dcb(**input_dct)  # Your download function
        except Exception as e:
            verboseprint(f"Error: {str(e)}", file=sys.stderr)
            status = 50  # Error status code
        else:
            if not status:
                print(f"Downloaded DCB Information File: {remote} as {local}")
                sys.exit(0)
    
        if attempt < MAX_RETRIES:
            verboseprint(f"Retrying in {SLEEP_DURATION} seconds...", file=sys.stderr)
            time.sleep(SLEEP_DURATION)

    # If all retries fail
    print("[ERROR] Failed to download DCB product after multiple attempts", file=sys.stderr)
    sys.exit(status)
