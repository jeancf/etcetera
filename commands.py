# -*- coding: utf-8 -*-
# Library of commands and support functions
# Maintainer JC Francois <jc.francois@gmail.com>


import sys
import os
import filecmp
import glob

from toolbox import *


def do_display_list(config, show=True):
    """
    Display the list of files currently managed by etcetera
    :param config: configuration object
    :param show: actually print list
    :return: number of files managed
    """
    n = 0
    # build list of all files in shadow location
    for directory, subdirectories, files in os.walk(config['MAIN']['SHADOW_LOCATION']):
        for file in files:
            # Consider files that do not have the .ORIG or the .SAVE extension
            if '.ORIG' not in file and '.COMMIT' not in file and '.COMMENT' not in file:
                # remove shadow location from full path to get the original location
                shadow_file = os.path.join(directory, file)
                origin = shadow_file.replace(config['MAIN']['SHADOW_LOCATION'], '')
                # Check that symlink exists in original location
                if os.path.islink(origin):
                    # Check that the symlink points to shadow_file
                    if os.readlink(origin) == shadow_file:
                        n += 1
                        if show:
                            print(' ' + origin)
    if show:
        print('Number of files managed: ' + str(n))
    return n


def do_manage_file(config, etc_file):
    """
    Move file from ORIGINAL_LOCATION to SHADOW_LOCATION and replace it by a symlink
    :param config:   Configuration object
    :param etc_file: Full path + name of the file to take over
    :return:
    """
    # Check if file is in allowed original locations
    if not is_in_original_locations(config, etc_file):
        print('ERROR: File is not in allowed original location')
        sys.exit(-1)

    # Check that file is not is blacklist
    if is_in_blacklist(config, etc_file):
        print('ERROR: File is blacklisted directly or in a blacklisted location in etcetera.conf')
        sys.exit(-1)

    # Check that the file exists
    if not os.path.isfile(etc_file):
        print('ERROR: File does not exist')
        sys.exit(-1)

    # Create file path in shadow location if necessary
    shadow_file = os.path.join(config['MAIN']['SHADOW_LOCATION'] + etc_file)
    shadow_path = os.path.dirname(shadow_file)
    os.makedirs(shadow_path, mode=0o755, exist_ok=True)

    # Check that file does not exist yet in shadow location
    if os.path.isfile(shadow_file):
        print('ERROR: File already managed')
        sys.exit(-1)

    # Move file to manage to shadow path and create copies with .COMMIT and .ORIG (if required) extension
    os.rename(etc_file, shadow_file)
    copy_file_with_stats(shadow_file, shadow_file + '.COMMIT')
    if config['BEHAVIOR'].getboolean('MANAGE_KEEP_ORIG'):
        copy_file_with_stats(shadow_file, shadow_file + '.ORIG')

    # Create symlink to shadow file in original location to replace  file to manage
    os.symlink(shadow_file, etc_file)

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
        print('Unmanage operation aborted.')
        sys.exit(-1)

    shadow_file = config['MAIN']['SHADOW_LOCATION'].rstrip('/') + symlink

    # Delete symlink and replace it by shadow file in original location
    os.remove(symlink)
    os.rename(shadow_file, symlink)

    # Optionally place a copy of .ORIG file in original location
    if config['BEHAVIOR'].getboolean('UNMANAGE_RESTORE_ORIG') and os.path.isfile(shadow_file + '.ORIG'):
        os.rename(shadow_file + '.ORIG', symlink + '.ORIG')

    # Delete all related files under shadow directory
    for f in glob.glob(shadow_file + '*'):
        os.remove(f)

    # Delete potential empty folders after removal of files
    remove_empty_directories(config, os.path.dirname(shadow_file))
    print('SUCCESS: File restored in original location and shadow content deleted')


def do_commit_file(config, symlink, note):
    """
    Save a copy of the managed file with .COMMIT extension and a timestamp
    If --note command is present, store text in .COMMENT extension and the same timestamp
    :param config:   Configuration object
    :param note:     Text to store in .COMMENT file
    :return:
    """
    # Check if symlink is managed correctly
    if not is_managed(config, symlink):
        print('Commit aborted.')
        sys.exit(-1)

    # Check if there are changes to commit
    timestamp = get_timestamp()
    shadow_file = config['MAIN']['SHADOW_LOCATION'].rstrip('/') + symlink
    commit_file = shadow_file + '.COMMIT'

    if filecmp.cmp(shadow_file, commit_file, shallow=True):
        print("NOTICE: No unrecorded changes. Nothing to do.")
        sys.exit(-1)

    # Check if a note is required and provided
    if config['BEHAVIOR'].getboolean('COMMIT_NOTE_REQUIRED') and note is None:
        print('ERROR: Configuration requires a note with every commit. Retry with --note "TEXT".')
        sys.exit(-1)

    # Create the .COMMIT file
    copy_file_with_stats(shadow_file, commit_file + timestamp)
    copy_file_with_stats(shadow_file, commit_file)

    # Write message to file
    if note is not None:
        with open(shadow_file + '.COMMENT' + timestamp, 'w') as comment_file:
            comment_file.write(note)

    # Delete oldest save files in excess of max allowed number
    save_file_list = glob.glob(commit_file + '_*')
    save_file_list.sort(reverse=True)
    for i in range(config['BEHAVIOR'].getint('COMMIT_MAX_SAVES'), len(save_file_list)):
        os.remove(save_file_list[i])
        try:
            os.remove(save_file_list[i].replace('.COMMIT', '.COMMENT'))
        except FileNotFoundError:
            pass

    print('SUCCESS: version committed')


def do_revert_file(config, symlink):
    # Check if symlink is managed correctly
    if not is_managed(config, symlink):
        print('Revert aborted.')
        sys.exit(-1)

    shadow_file = os.path.join(config['MAIN']['SHADOW_LOCATION'] + symlink)

    # Display list of dates
    print('File was committed on these dates:')
    file_list = get_file_list(config, symlink)
    i = 0
    for f in file_list:
        i += 1
        if '.ORIG' in f[0]:
            # Print original file datestamp
            print(' {:>4}'.format(str(i)) + ' | ' + f[1] + ' | (original file)')

        else:
            # Print saved file timestamp and related note
            note = ''
            try:
                nf = open(f[0].replace('.COMMIT', '.COMMENT'), 'r')
                note = nf.readline()
            except FileNotFoundError:
                pass
            finally:
                nf.close()
            print(' {:>4}'.format(str(i)) + ' | ' + f[1] + ' | ' + note)

    choice = input('Select file version to revert to (1-' + str(i) + ', 0 to abort): ')

    try:
        num_choice = int(choice)
    except ValueError:
        print('ERROR: invalid input')
        sys.exit(-1)

    if num_choice == 0:
        print('NOTICE: Aborted by user')
        sys.exit(0)
    elif 0 < num_choice <= i:
        # Revert to selected file
        shutil.copy2(file_list[num_choice-1][0], shadow_file)
    else:
        print('ERROR: invalid input')
        sys.exit(-1)

    print('SUCCESS: selected version restored')


def do_display_file_status(config, symlink):
    # Check if symlink is managed correctly
    if not is_managed(config, symlink):
        print('Incorrect setup. Try "--unmanage" then "--manage" again to reset')
        sys.exit(-1)

    shadow_file = config['MAIN']['SHADOW_LOCATION'].rstrip('/') + symlink
    commit_file = shadow_file + '.COMMIT'

    # List save dates of .COMMIT and .ORIG files
    print('File was committed on these dates:')
    file_list = get_file_list(config, symlink)
    i = 0
    for f in file_list:
        i += 1
        if '.ORIG' in f[0]:
            # Print original file datestamp
            print(' {:>4}'.format(str(i)) + ' | ' + f[1] + ' | (original file)')

        else:
            # Print saved file timestamp and related note
            try:
                with open(f[0].replace('.COMMIT', '.COMMENT'), 'r') as nf:
                    note = nf.readline()
            except FileNotFoundError:
                note = ''
            print(' {:>4}'.format(str(i)) + ' | ' + f[1] + ' | ' + note)

    # Check if there are uncommitted changes
    if filecmp.cmp(shadow_file, commit_file, shallow=True):
        print("\nThere are no uncommited changes to the file")
    else:
        print("\nSome changes to the file are not committed")


def do_display_info(config):
    # Config file location
    print('Location of config file:')
    print(' /etc/etcetera.conf')

    # Locations being monitored
    print('Locations where files can be monitored:')
    mon_locs = config['MAIN']['ORIGINAL_LOCATIONS'].split(' ')
    i = 0
    for loc in mon_locs:
        if loc != '':
            print(' ' + loc)

    # Shadow location
    print('Location of shadow files:')
    print(' ' + str(config['MAIN']['SHADOW_LOCATION']))

    # Number of managed files
    print('Number of files managed: ' + str(do_display_list(config, show=False)))

    # Max number of backups preserved for each file
    print('Max. number of backups preserved for each file: ' + str(config['BEHAVIOR']['COMMIT_MAX_SAVES']))

    # Original files
    print('Original files are preserved: ' + str(config['BEHAVIOR'].getboolean('MANAGE_KEEP_ORIG')))