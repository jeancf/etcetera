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
cmdline = argparse.ArgumentParser(prog='etcetera', description='Manage config files with style.')
# parser.add_argument('filename', nargs='?', action='store', help='Name of file to manage')
cmdline.add_argument('-l', '--list', action='store_true', help='List files managed by etcetera')
cmdline.add_argument('-m', '--manage', metavar='filename', action='store', help='take over file and replace by symlink in /etc')
cmdline.add_argument('-u', '--unmanage', metavar='filename', action='store', help='return file to /etc')

# Parse command line arguments
args = vars(cmdline.parse_args()) # convert namespace object to dictionary

# DEBUG
print(args)

# TODO: Respond to commands
if args['list'] == True:
    print('TODO: DISPLAY LIST')
elif args['manage'] != None:
    print('TODO: MANAGE ' + args['manage'])
elif args['unmanage'] != None:
    print('TODO: UNMANAGE ' + args['unmanage'])
else:
    print('Check available commands with "etcetera -h"')