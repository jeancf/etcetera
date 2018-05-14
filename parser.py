#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Command line executable

"""
    Copyright (C) 2018  Jean-Christophe Francois

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import argparse
import configparser


# Confirm that we have root privileges
if os.geteuid() != 0:
    print('ERROR: You do not have elevated privileges. Try "sudo etcetera"')
    sys.exit(-1)

CONFIG_FILE_LOCATION = './etcetera.conf'

# Add path to etcetera modules
sys.path.append('/usr/lib/etcetera')

from commands import *

# Check that config file exists
config = None
if os.path.isfile(CONFIG_FILE_LOCATION):
    # Parse config file
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_LOCATION)

    # DEBUG
    # for key in config['MAIN']:
    #      print(str(key) + " = " + str(config['MAIN'][key]))
    # for key in config['BEHAVIOR']:
    #     print(str(key) + " = " + str(config['BEHAVIOR'][key]))

else:
    print('ERROR: config file ' + CONFIG_FILE_LOCATION + ' not found.')
    exit(-1)

# Configure command line arguments parser
cmdline = argparse.ArgumentParser(prog='etcetera', description='Config file management with a touch of wisdom.')
# parser.add_argument('FILENAME', nargs='?', action='store', help='Name of file to manage')
cmdline.add_argument('-l', '--list', action='store_true',
                     help='List files managed by etcetera')
cmdline.add_argument('-m', '--manage', metavar='FILENAME', action='store',
                     help='Full path of file to take over and replace by symlink')
cmdline.add_argument('-u', '--unmanage', metavar='FILENAME', action='store',
                     help='Full path of file to return to original location instead of symlink')
cmdline.add_argument('-c', '--commit', metavar='FILENAME', action='store',
                     help='Full path of symlink to managed file to save')
cmdline.add_argument('-n', '--note', metavar='"TEXT"', action='store',
                     help='one-line note between quote marks to store with the committed file\
                           (only considered together with --commit)')
cmdline.add_argument('-r', '--revert', metavar='FILENAME', action='store',
                     help='Full path of symlink to managed file to restore')
cmdline.add_argument('-s', '--status', metavar='FILENAME', action='store',
                     help='Full path of symlink for which to display status')
cmdline.add_argument('-i', '--info', action='store_true',
                     help='Display info about etcetera config and state')

# Parse command line arguments
args = vars(cmdline.parse_args())  # convert namespace object to dictionary

# DEBUG
# print(args)

# Respond to commands
if args['list']:
    do_display_list(config)
elif args['manage'] is not None:
    do_manage_file(config, args['manage'])
elif args['unmanage'] is not None:
    do_unmanage_file(config, args['unmanage'])
elif args['commit'] is not None:
        do_commit_file(config, args['commit'], args['note'])
elif args['revert'] is not None:
    do_revert_file(config, args['revert'])
elif args['status'] is not None:
    do_display_file_status(config, args['status'])
elif args['info']:
    do_display_info(config)
else:
    print('Check available commands with "etcetera -h"')
