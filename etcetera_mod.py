# -*- coding: utf-8 -*-
# Library of commands and support functions
# Maintainer JC Francois <jc.francois@gmail.com>

def validate_filename():
    # TODO Check if the filename is under ORIGINAL_LOCATION
    # TODO Check if the filename is in blacklist
    print('TODO: VALIDATE FILENAME')

def display_list():
    '''
    Display the list of files currently managed by etcetera
    :return: 
    '''
    print('TODO: DISPLAY LIST')


def manage_file(filename):
    '''
    Move file from ORIGINAL_LOCATION to SHADOW_LOCATION
    and replace it by a symlink.
    :param filename: Full path + name of the file to take over.
                     By extension, can also be a directory (e.g. /etc/ssh/)
    :return: 
    '''
    print('TODO: MANAGE ' + filename)


def unmanage_file(filename):
    '''
    Restore file from SHADOW_LOCATION to ORIGINAL_LOCATION
    :param filename: Full path + name of the file to restore.
                     By extension, can also be a directory (e.g. /etc/ssh/)
    :return: 
    '''
    print('TODO: UNMANAGE ' + filename)
