#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Maintainer JC Francois <jc.francois@gmail.com>

import os
import sys
import argparse
import configparser
from etcetera_mod import *

# Check that we have root privileges
if os.geteuid() != 0:
    print('You do not have elevated privileges. Please run etcetera as root')
    sys.exit(-1)

# Configure command line arguments parser
cmdline = argparse.ArgumentParser(prog='etcetera', description='Manage config files with wisdom.')
# parser.add_argument('filename', nargs='?', action='store', help='Name of file to manage')
cmdline.add_argument('-l', '--list', action='store_true',
                     help='List files managed by etcetera')
cmdline.add_argument('-m', '--manage', metavar='filename', action='store',
                     help='Full path of file to take over and replace by symlink')
cmdline.add_argument('-u', '--unmanage', metavar='filename', action='store',
                     help='Full path of file to return to original location instead of symlink')

# Parse command line arguments
args = vars(cmdline.parse_args()) # convert namespace object to dictionary

# DEBUG
print(args)

# Respond to commands
if args['list'] == True:
    display_list()
elif args['manage'] != None:
    manage_file(args['manage'])
elif args['unmanage'] != None:
    unmanage_file(args['unmanage'])
else:
    print('Check available commands with "etcetera -h"')
