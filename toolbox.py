# -*- coding: utf-8 -*-
# Library of commands and support functions
# Maintainer JC Francois <jc.francois@gmail.com>

import os
import time
import shutil
import glob


CONST_TIMESTAMP_FORMAT_STRING = '_%Y-%m-%d_%H-%M-%S'


def is_in_original_locations(config, file):
    """
    Verify if file is located in directory listed under ORIGINAL_LOCATIONS in config file
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


def is_in_blacklist(config, file):
    """
    Verify if file is listed directly or in a directory under BLACKLIST in config file
    :param config:  Configuration object
    :param file:    full path + name of file or symlink to check
    :return: True or False
    """
    blacklist = config['MAIN']['BLACKLIST'].split(' ')
    for blacklisted in blacklist:
        if blacklisted != '' and file.find(blacklisted) >= 0:
            return True
    return False


def is_managed(config, symlink):
    """
    Verify that the symlink is correctly managed
    :param config:  Configuration object
    :param symlink: full path + name of symlink to check
    :return: True or False
    """
    # Check if symlink is in allowed original locations
    if not is_in_original_locations(config, symlink):
        print('ERROR: File is not in an allowed original location')
        return False

    # Check that the file is a symlink
    if not os.path.islink(symlink):
        print('ERROR: Argument is not a symlink')
        return False

    # Check that the symlink points to the correct file in shadow location
    shadow_file = config['MAIN']['SHADOW_LOCATION'].rstrip('/') + symlink
    if os.readlink(symlink) != shadow_file:
        print('ERROR: Symlink does not point to correct shadow file')
        return False

    # Check that the corresponding shadow file exists
    if not os.path.isfile(shadow_file):
        print('ERROR: Shadow file does not exit')
        return False

    # Check that the corresponding .COMMIT is present
    if not os.path.isfile(shadow_file):
        print('ERROR: Commit file does not exit')
        return False

    return True


def copy_file_with_stats(source, destination):
    shutil.copy2(source, destination)
    # Make sure file stats are identical as they are used for change detection
    shutil.copystat(source, destination)


def remove_empty_directories(config, directory):
    """
    Remove empty directories as far up directory as possible
    :param config:    Configuration object
    :param directory: Full path of directory to consider
    :return:
    """
    # Verify that we are within SHADOW_LOCATION
    shadow_location = config['MAIN']['SHADOW_LOCATION'].rstrip('/')
    if directory.startswith(shadow_location):
        path = directory.rstrip('/')
        while path != shadow_location:
            if len(os.listdir(path)) == 0:  # Directory is empty
                os.rmdir(path)  # No risk of apocalypse as rmdir only works on empty directories
            path = os.path.dirname(path)


def get_timestamp():
    """
    Get localtime and format timestamp string to append to file e.g. 20180105_105622
    :param:
    :return: string formatted to be used in files extension
    """
    return time.strftime(CONST_TIMESTAMP_FORMAT_STRING, time.localtime())


def get_timestring_from_timestamp(timestamp):
    """
    Returns  string with date and time from timestamp e.g. "Fri Jan  5 10:56:22 2018"
    :param:  timestamp created with get_timestamp()
    :return: string with date and time from timestamp
    """
    return time.asctime(time.strptime(timestamp, CONST_TIMESTAMP_FORMAT_STRING))


def get_file_list(config, symlink):
    """
    Returns  string with date and time from timestamp e.g. "Fri Jan  5 10:56:22 2018"
    :param:  timestamp created with get_timestamp()
    :return: list of .COMMIT files and .ORIG file along with their timestamp formatted for display
    """
    shadow_file = os.path.join(config['MAIN']['SHADOW_LOCATION'] + symlink)
    commit_file = shadow_file + '.COMMIT'
    original_file = shadow_file + '.ORIG'

    # Build list of candidate files for restoration
    file_list = glob.glob(commit_file + '_*')
    file_list.sort(reverse=True)

    # build list of files and dates of COMMIT files
    full_list = []
    i = 0
    for fn in file_list:
        i += 1
        # Extract timestamp from file name and transform it into a printable string
        timestring = get_timestring_from_timestamp(fn.split('.COMMIT', maxsplit=1)[1])
        full_list.append((fn, timestring))

    # Add .ORIG file and date to the list if it exits
    if os.path.isfile(original_file):
        i += 1
        # Convert the mtime from file stat into time tuple then into readable string
        timestring = time.asctime(time.localtime(os.stat(original_file).st_mtime))
        full_list.append((original_file, timestring))

    return full_list
