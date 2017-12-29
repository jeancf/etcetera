#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import argparse
import configparser
from etcetera_mod import *

# Check that we have root privilieges
if os.geteuid() != 0:
    print('You do not have elevated privileges. Please run etcetera as root')
    sys.exit(-1)

# Configure command line arguments parser
cmdline = argparse.ArgumentParser(prog='etcetera', description='Manage config files with style.')
# parser.add_argument('filename', nargs='?', action='store', help='Name of file to manage')
cmdline.add_argument('-l', '--list', action='store_true', help='List files managed by etcetera')
cmdline.add_argument('-m', '--manage', metavar='filename', action='store', help='take over file and replace by symlink in /etc')
cmdline.add_argument('-u', '--unmanage', metavar='filename', action='store', help='return file to /etc')

# Parse command line arguments
args = cmdline.parse_args()

# DEBUG
print(args)
