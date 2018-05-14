# -*- coding: utf-8 -*-
# Library of commands

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

import sys
import os
import glob

# Add path to etcetera modules
sys.path.append('/usr/lib/etcetera')

from toolbox import *


def do_display_list(config, show=True):
    """
    Display the list of files currently managed by etcetera
    :param config: configuration object
    :param show: actually print list
    :return: number of files managed
    """

    if show:
        print('Files managed by etcetera:')

    n = 0

    # build list of all files in managed location
    for directory, subdirectories, files in os.walk(config['MAIN']['MANAGED_LOCATION']):
        for file in files:
            # Consider files that do not have the .ORIG or the .SAVE extension
            if '.ORIG' not in file and '.COMMIT' not in file and '.COMMENT' not in file:
                # remove managed location from full path to get the original location
                managed_file = os.path.join(directory, file)
                origin = managed_file.replace(config['MAIN']['MANAGED_LOCATION'], '')
                # Check that symlink exists in original location
                if os.path.islink(origin):
                    # Check that the symlink points to managed_file
                    if os.readlink(origin) == managed_file:
                        n += 1
                        if show:
                            print(' ' + origin)

    if show:
        print('Number of files managed: ' + str(n))

    return n


def do_manage_file(config, etc_file):
    """
    Move file from ORIGINAL_LOCATION to MANAGED_LOCATION and replace it by a symlink
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

    # Create file path in managed location if necessary
    managed_file = os.path.join(config['MAIN']['MANAGED_LOCATION'] + etc_file)
    managed_path = os.path.dirname(managed_file)
    os.makedirs(managed_path, mode=0o755, exist_ok=True)

    # Check that file does not exist yet in managed location
    if os.path.isfile(managed_file):
        print('ERROR: File already managed')
        sys.exit(-1)

    # Move file to manage to managed path and create copies with .COMMIT and .ORIG (if required) extension
    os.rename(etc_file, managed_file)
    copy_file_with_stats(managed_file, managed_file + '.COMMIT')
    if config['BEHAVIOR'].getboolean('MANAGE_KEEP_ORIG'):
        copy_file_with_stats(managed_file, managed_file + '.ORIG')

    # Create symlink to managed file in original location to replace  file to manage
    os.symlink(managed_file, etc_file)

    print('SUCCESS: File saved and replaced by symlink')


def do_unmanage_file(config, symlink):
    """
    Restore file from MANAGED_LOCATION to ORIGINAL_LOCATION
    :param config:        Configuration object
    :param symlink:       Full path + name of the symlink to replace with file
    :return:
    """
    # Check if symlink is in allowed original locations
    if not is_managed(config, symlink):
        print('Unmanage operation aborted.')
        sys.exit(-1)

    managed_file = config['MAIN']['MANAGED_LOCATION'].rstrip('/') + symlink

    # Delete symlink and replace it by managed file in original location
    os.remove(symlink)
    os.rename(managed_file, symlink)

    # Optionally place a copy of .ORIG file in original location
    if config['BEHAVIOR'].getboolean('UNMANAGE_RESTORE_ORIG') and os.path.isfile(managed_file + '.ORIG'):
        os.rename(managed_file + '.ORIG', symlink + '.ORIG')

    # Delete all related files under managed directory
    for f in glob.glob(managed_file + '*'):
        os.remove(f)

    # Delete potential empty folders after removal of files
    remove_empty_directories(config, os.path.dirname(managed_file))
    print('SUCCESS: File restored in original location and managed content deleted')


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

    timestamp = get_timestamp()
    managed_file = config['MAIN']['MANAGED_LOCATION'].rstrip('/') + symlink
    commit_file = managed_file + '.COMMIT'
    # Check if there are changes to commit
    if not is_different(managed_file, commit_file):
        print("NOTICE: No unrecorded changes. Nothing to do.")
        sys.exit(-1)

    # Check if a note is required and provided
    if config['BEHAVIOR'].getboolean('COMMIT_NOTE_REQUIRED') and note is None:
        print('ERROR: Configuration requires a note with every commit. Retry with --note "TEXT".')
        sys.exit(-1)

    # Create the .COMMIT file
    copy_file_with_stats(managed_file, commit_file + timestamp)
    copy_file_with_stats(managed_file, commit_file)

    # Write message to file
    if note is not None:
        with open(managed_file + '.COMMENT' + timestamp, 'w') as comment_file:
            comment_file.write(note)

    # Delete oldest commit files in excess of max allowed number
    commit_file_list = glob.glob(commit_file + '_*')
    commit_file_list.sort(reverse=True)
    for i in range(config['BEHAVIOR'].getint('COMMIT_MAX_SAVES'), len(commit_file_list)):
        os.remove(commit_file_list[i])
        try:
            os.remove(commit_file_list[i].replace('.COMMIT', '.COMMENT'))
        except FileNotFoundError:
            pass

    print('SUCCESS: version committed')


def do_revert_file(config, symlink):
    # Check if symlink is managed correctly
    if not is_managed(config, symlink):
        print('Revert aborted.')
        sys.exit(-1)

    managed_file = os.path.join(config['MAIN']['MANAGED_LOCATION'] + symlink)
    commit_file = managed_file + '.COMMIT'

    # Display list of commits
    print('File was committed on these dates:')
    file_list = get_file_list(config, symlink)
    i = len(file_list) + 1
    for f in file_list:
        i -= 1
        if '.ORIG' in f[0]:
            # Print original file datestamp
            print(' {:>4}'.format(str(i)) + ' | ' + f[1] + ' | ' + f[2] + ' | ' + f[3] + ' | (original file)')

        else:
            # Print commit file timestamp and related note
            note = ''
            try:
                nf = open(f[0].replace('.COMMIT', '.COMMENT'), 'r')
                note = nf.readline()
            except FileNotFoundError:
                pass
            finally:
                nf.close()
            print(' {:>4}'.format(str(i)) + ' | ' + f[1] + ' | ' + f[2] + ' | ' + f[3] + ' | ' + note)

    # Check if there are uncommitted changes
    if is_different(managed_file, commit_file):
        print("\nWARNING: Some changes to the file are not committed.")
        print("         If you revert now they will be overwritten.\n")

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
        # Revert selected file
        file_idx = len(file_list) - num_choice
        copy_file_with_stats(file_list[file_idx][0], managed_file)

    else:
        print('ERROR: invalid input')
        sys.exit(-1)

    print('SUCCESS: selected version restored')


def do_display_file_status(config, symlink):
    # Check if symlink is managed correctly
    if not is_managed(config, symlink):
        print('Incorrect setup. Try "--unmanage" then "--manage" again to reset')
        sys.exit(-1)

    managed_file = config['MAIN']['MANAGED_LOCATION'].rstrip('/') + symlink
    commit_file = managed_file + '.COMMIT'

    # List save dates of .COMMIT and .ORIG files
    print('File was committed on these dates:')
    file_list = get_file_list(config, symlink)
    i = len(file_list) + 1
    for f in file_list:
        i -= 1
        if '.ORIG' in f[0]:
            # Print original file datestamp
            print(' {:>4}'.format(str(i)) + ' | ' + f[1] + ' | ' + f[2] + ' | ' + f[3] + ' | (original file)')

        else:
            # Print commit file timestamp and related note
            try:
                with open(f[0].replace('.COMMIT', '.COMMENT'), 'r') as nf:
                    note = nf.readline()
            except FileNotFoundError:
                note = ''
            print(' {:>4}'.format(str(i)) + ' | ' + f[1] + ' | ' + f[2] + ' | ' + f[3] + ' | ' + note)

    # Check if there are uncommitted changes
    if is_different(managed_file, commit_file):
        print("\nSome changes to the file are not committed")
    else:
        print("\nThere are no uncommited changes to the file")


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
    print('Location of managed files:')
    print(' ' + str(config['MAIN']['MANAGED_LOCATION']))

    # Number of managed files
    print('Number of files managed: ' + str(do_display_list(config, show=False)))

    # Max number of backups preserved for each file
    print('Max. number of backups preserved for each file: ' + str(config['BEHAVIOR']['COMMIT_MAX_SAVES']))

    # Original files
    print('Original files are preserved: ' + str(config['BEHAVIOR'].getboolean('MANAGE_KEEP_ORIG')))