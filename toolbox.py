# -*- coding: utf-8 -*-
# Library of commands and support functions
# Maintainer JC Francois <jc.francois@gmail.com>

import os


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