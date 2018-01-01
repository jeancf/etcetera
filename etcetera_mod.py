# -*- coding: utf-8 -*-
# Library of commands and support functions
# Maintainer JC Francois <jc.francois@gmail.com>

import sys
import os
import glob
import shutil

# ---------------------------------------------------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------------------------------------------------


def display_list(config):
    """
    Display the list of files currently managed by etcetera
    :param config: Configuration object
    :return: 
    """
    # build list of all files in shadow location
    for directory, subdirectories, files in os.walk(config['MAIN']['SHADOW_LOCATION']):
        for file in files:
            # Consider files that do not have the .ORIG or the .SAVE extension
            if not '.ORIG' in file and not '.SAVE' in file:
                # remove shadow location from full path to get the original location
                shadow_file = os.path.join(directory, file)
                origin = shadow_file.replace(config['MAIN']['SHADOW_LOCATION'], '')
                # Check that symlink exists in original location
                if os.path.islink(origin):
                    # Check that the symlink points to shadow_file
                    if os.readlink(origin) == shadow_file:
                        print(origin)

def manage_file(config, original_file):
    """
    Move file from ORIGINAL_LOCATION to SHADOW_LOCATION and replace it by a symlink
    :param config:        Configuration object
    :param original_file: Full path + name of the file to take over
    :return:
    """
    # Check if file is in allowed original locations
    if not is_in_original_locations(config, original_file):
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

    # Create file path in shadow location if necessary
    shadow_file = config['MAIN']['SHADOW_LOCATION'].rstrip('/') + original_file
    shadow_path = os.path.dirname(shadow_file)
    os.makedirs(shadow_path, mode=0o755, exist_ok=True)

    # Check that file does not exist yet in shadow location
    if os.path.isfile(shadow_file):
        print('ERROR: File already managed')
        sys.exit(-1)

    # Move original file to shadow path and create a copy with .ORIG extension if required
    os.rename(original_file, shadow_file)
    if config['BEHAVIOR'].getboolean('KEEP_ORIG'):
        shutil.copy2(shadow_file, shadow_file + '.ORIG')

    # Create symlink to shadow file in original location to replace original file
    os.symlink(shadow_file, original_file)

    print('SUCCESS: File saved and replaced by symlink')


def unmanage_file(config, symlink):
    """
    Restore file from SHADOW_LOCATION to ORIGINAL_LOCATION
    :param config:        Configuration object
    :param symlink:       Full path + name of the symlink to replace with file
    :return:
    """
    # Check if symlink is in allowed original locations
    if not is_in_original_locations(config, symlink):
        print('ERROR: File is not in allowed original location')
        sys.exit(-1)

    # Check that the file is a symlink
    if not os.path.islink(symlink):
        print('ERROR: Argument is not a symlink')
        sys.exit(-1)

    # Check that the symlink points to the correct file in shadow location
    shadow_file = config['MAIN']['SHADOW_LOCATION'].rstrip('/') + symlink
    if os.path.realpath(symlink) != shadow_file:
        print('ERROR: Symlink does not point to correct shadow file (names do not match)')
        sys.exit(-1)

    # Check that the corresponding shadow file exists
    if not os.path.isfile(shadow_file):
        print('ERROR: Shadow file does not exit')
        sys.exit(-1)

    # Delete symlink and replace it by shadow file in original location
    os.remove(symlink)
    os.rename(shadow_file, symlink)

    # Optionally place a copy of .ORIG file in original location
    if config['BEHAVIOR'].getboolean('RESTORE_ORIG') and os.path.isfile(shadow_file + '.ORIG'):
        os.rename(shadow_file + '.ORIG', symlink + '.ORIG')

    # Delete all related files under shadow directory
    for f in glob.glob(shadow_file + '*'):
        os.remove(f)

    # Delete potential empty folders after removal of files
    remove_empty_directories(os.path.dirname(shadow_file))
    print('SUCCESS: File restored in original location and shadow content deleted')


# ---------------------------------------------------------------------------------------------------------------------
# Utils
# ---------------------------------------------------------------------------------------------------------------------


def is_in_original_locations(config, file):
    """
    Verify is file is located in directory listed under ORIGINAL_LOCATIONS in config file
    :param config:  Configuration object
    :param file:    full path + name of file or symlink to check 
    :return: True or False
    """
    locations = config['MAIN']['ORIGINAL_LOCATIONS'].split(' ')
    valid = False
    for loc in locations:
        if loc != '' and file.startswith(loc):
            valid = True
    return valid


def remove_empty_directories(directory):
    """
    Remove empty directories as far up full_path as possible
    :param directory: Full path of directory to consider
    :return:
    """
    path = directory
    while path != '/':
        if len(os.listdir(path)) == 0:  # Directory is empty
            os.rmdir(path)  # rmdir only works on empty directories
        path = os.path.dirname(path)
