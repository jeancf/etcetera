#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Command line executable
# Maintainer JC Francois <jc.francois@gmail.com>

import argparse
import configparser

from commands import *


# Check that we have root privileges
if os.geteuid() != 0:
    print('ERROR: You do not have elevated privileges. Try "sudo etcetera"')
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
# print(args)

# Parse config file
config = configparser.ConfigParser()
config.read('etcetera.conf')

# DEBUG
# for key in config['MAIN']:
#     print(str(key) + " = " + str(config['MAIN'][key]))

# Respond to commands
if args['list']:
    display_list(config)
elif args['manage'] is not None:
    manage_file(config, args['manage'])
elif args['unmanage'] is not None:
    unmanage_file(config, args['unmanage'])
else:
    print('Check available commands with "etcetera -h"')
