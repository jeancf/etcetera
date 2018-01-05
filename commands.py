# -*- coding: utf-8 -*-
# Library of commands and support functions
# Maintainer JC Francois <jc.francois@gmail.com>


import sys
import os
import glob
import filecmp

from toolbox import *


def do_display_list(config):
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


def do_manage_file(config, original_file):
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
    if is_in_blacklist(config, original_file):
        print('ERROR: File is blacklisted directly or in a blacklisted location in etcetera.conf')
        sys.exit(-1)

    # Check that the file exists
    if not os.path.isfile(original_file):
        print('ERROR: File does not exist')
        sys.exit(-1)

    # Create file path in shadow location if necessary
    shadow_file = os.path.join(config['MAIN']['SHADOW_LOCATION'] + original_file)
    shadow_path = os.path.dirname(shadow_file)
    os.makedirs(shadow_path, mode=0o755, exist_ok=True)

    # Check that file does not exist yet in shadow location
    if os.path.isfile(shadow_file):
        print('ERROR: File already managed')
        sys.exit(-1)

    # Move original file to shadow path and create copies with .COMMIT and .ORIG (if required) extension
    os.rename(original_file, shadow_file)
    copy_file_with_stats(shadow_file, shadow_file + '.COMMIT')
    if config['BEHAVIOR'].getboolean('KEEP_ORIG'):
        copy_file_with_stats(shadow_file, shadow_file + '.ORIG')

    # Create symlink to shadow file in original location to replace original file
    os.symlink(shadow_file, original_file)

    print('SUCCESS: File saved and replaced by symlink')


def do_unmanage_file(config, symlink):
    """
    Restore file from SHADOW_LOCATION to ORIGINAL_LOCATION
    :param config:        Configuration object
    :param symlink:       Full path + name of the symlink to replace with file
    :return:
    """
    # Check if symlink is in allowed original locations
    if not is_managed(config, symlink):
        print('unmanage operation aborted.')
        sys.exit(-1)

    shadow_file = config['MAIN']['SHADOW_LOCATION'].rstrip('/') + symlink

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


def do_commit_file(config, symlink):
    # Check if symlink is managed correctly
    if not is_managed(config, symlink):
        print('Commit aborted.')
        sys.exit(-1)

    shadow_file = config['MAIN']['SHADOW_LOCATION'].rstrip('/') + symlink
    commit_file = shadow_file + '.COMMIT'

    if filecmp.cmp(shadow_file, commit_file, shallow=True):
        print("NOTICE: No unrecorded changes. Nothing to do.")
        sys.exit(-1)

    copy_file_with_stats(shadow_file, commit_file + get_timestamp())
    copy_file_with_stats(shadow_file, commit_file)

    # Delete oldest save files in excess of max allowed number
    save_file_list = glob.glob(commit_file + '_*')
    save_file_list.sort(reverse=True)
    for i in range(config['BEHAVIOR'].getint('MAX_SAVES'), len(save_file_list)):
        os.remove(save_file_list[i])

    print('SUCCESS: version committed')


def do_revert_file(config, symlink):
    # Check if symlink is managed correctly
    if not is_managed(config, symlink):
        print('Revert aborted.')
        sys.exit(-1)

    shadow_file = os.path.join(config['MAIN']['SHADOW_LOCATION'] + symlink)
    commit_file = shadow_file + '.COMMIT'

    # Build list of candidate files for restoration
    save_file_list = glob.glob(commit_file + '_*')
    save_file_list.sort(reverse=True)

    # Display list of dates of COMMIT files and get user choice
    print('File was saved on these dates:')
    i = 0
    for fn in save_file_list:
        i += 1
        # Extract timestamp from file name and transform it into a printable string
        timestring = get_timestring_from_timestamp(fn.split('.COMMIT', maxsplit=1)[1])
        print(' {:>4}'.format(str(i)) + ' | ' + timestring)

    # Add .ORIG file to the list if it exits
    if os.path.isfile(shadow_file + '.ORIG'):
        i += 1
        # Convert the mtime from file stat into time tuple then into readable string
        timestring = time.asctime(time.localtime(os.stat(shadow_file + '.ORIG').st_mtime))
        print(' {:>4}'.format(str(i)) + ' | ' + timestring + ' (original file)')

    choice = input('Select file version to revert to (1-' + str(i) + ', 0 to abort): ')

    try:
        num_choice = int(choice)
    except ValueError:
        print('ERROR: invalid input')
        sys.exit(-1)

    if num_choice == 0:
        print('NOTICE: Aborted by user')
        sys.exit(0)
    elif num_choice == i:
        # Revert to .ORIG file
        shutil.copy2(shadow_file + '.ORIG', shadow_file)
    elif 0 < num_choice < i:
        # Revert to .COMMIT file
        shutil.copy2(save_file_list[num_choice-1], shadow_file)
    else:
        print('ERROR: invalid input')
        sys.exit(-1)

    print('SUCCESS: selected version restored')


def display_file_status(config, symlink):
    # Check if symlink is managed correctly
    if not is_managed(config, symlink):
        print('Incorrect setup. Try "--unmanage" then "--manage" again to reset')
        sys.exit(-1)
