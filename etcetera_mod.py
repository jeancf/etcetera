# -*- coding: utf-8 -*-
# Library of commands and support functions
# Maintainer JC Francois <jc.francois@gmail.com>

import sys
import os
import shutil
import time

def display_list(config):
    """
    Display the list of files currently managed by etcetera
    :param config: Configuration object
    :return: 
    """
    print('TODO: DISPLAY LIST')


def manage_file(config, original_file):
    """
    Move file from ORIGINAL_LOCATION to SHADOW_LOCATION and replace it by a symlink
    :param config:        Configuration object
    :param original_file: Full path + name of the file to take over
                          By extension, can also be a directory (e.g. /etc/ssh/)
    :return: 
    """
    # Check if file is in allowed original locations
    locations = config['MAIN']['ORIGINAL_LOCATIONS'].split(' ')
    valid = False
    for loc in locations:
        if loc != '' and original_file.startswith(loc):
            valid = True
    if not valid:
        print('ERROR: File is not in allowed original location')
        sys.exit(-1)

    # Check that file is not is blacklist
    blacklist = config['MAIN']['BLACKLIST'].split(' ')
    for blacklisted in blacklist:
        if original_file == blacklisted:
            print('ERROR: File is blacklisted in etcetera configuration')
            sys.exit(-1)

    # Check that the file exists
    if not os.path.isfile(original_file):
        print('ERROR: File does not exist')
        sys.exit(-1)

    # Make sure file path exists in shadow location
    original_path = os.path.dirname(original_file)
    shadow_file = config['MAIN']['SHADOW_LOCATION'].rstrip('/') + original_file
    shadow_path = os.path.dirname(shadow_file)
    os.makedirs(shadow_path, mode=0o755, exist_ok=True)

    # Check that file does not exist yet in shadow location
    if os.path.isfile(shadow_file):
        print('ERROR: File already managed')
        sys.exit(-1)

    # Move original file to shadow path and create a copy with .orig extension if required
    os.rename(original_file, shadow_file)
    if config['BEHAVIOR'].getboolean('STORE_ORIG'):
        shutil.copy2(shadow_file, shadow_file + '.orig')

    # Delete original file and replace by symlink to shadow file in original location
    os.symlink(shadow_file, original_file)

    print('SUCCESS: File saved and replaced by symlink')


def unmanage_file(config, filename):
    """
    Restore file from SHADOW_LOCATION to ORIGINAL_LOCATION
    :param config:   Configuration object
    :param filename: Full path + name of the file to restore
                     By extension, can also be a directory (e.g. /etc/ssh/)
    :return: 
    """
    print('TODO: UNMANAGE ' + filename)
