Etcetera
========

![etcetera-logo.png](etcetera-logo.png)

**Config file management with a touch of wisdom.**

## About ##

Etcetera is a simple command line tool that lets you keep track of changes to
config files of a linux system.
It is loosely inspired from the basic functionality of git (commit and revert).

## Why Etcetera? ##

When I configure or troubleshoot a system I make sometimes a lot of changes to
config files, some good, some that need to be reverted because they do not have
the intended effect. In the heat of the action, it is easy to lose track of
what change has been made to what file.

I started etcetera to address that issue. With it I keep a copy of the untouched
original file and I preserve changes that I make associated with a note that
helps me remember what I have done. And just by looking at what file etcetera
manages, I can tell exactly what packages use configuration that deviates from
installation defaults.

## Features ##

* Strictly define locations where files can be managed by Etcetera
* Select which files to manage
* Commit changes made to a managed file with associated note
* Revert changes by selecting a previous commit
* Restore managed file back to the original location
* Colorized output (off by default)

## Download and install ##

### Archlinux ###

The `etcetera` package is available in the AUR.

### Manual installation ###

Clone the project or download and unpack the zip file from github.

First `cd` into the directory where you unpacked the zip

Make sure `./install-etcetera.sh` is executable:

    $ sudo chmod u+x ./install-etcetera.sh

Then run:
   
    $ sudo ./install-etcetera.sh
    
To uninstall later, run:

    $ sudo /usr/share/install-etcetera.sh --remove

For information, the install script copies project files to the following
locations on your system:

| File                | Location                      | Mode |
|---------------------|-------------------------------|------|
| `etcetera`          | `/usr/bin`                    | 755  |
| `parser.py`         | `/usr/lib/etcetera`           | 755  |
| `commands.py`       | `/usr/lib/etcetera`           | 640  |
| `toolbox.py`        | `/usr/lib/etcetera`           | 640  |
| `term_colors.py`    | `/usr/lib/etcetera`           | 640  |
| `etcetera-logo.png` | `/usr/share/etcetera`         | 640  |
| `etcetera.conf`     | `/etc/etcetera/etcetera.conf` | 640  |

It makes sure they are all owned by `root:root` and have the correct mode set.

## Documentation ##

### Getting Started ###

Let's assume that we want to manage and track the configuration of the
network time protocol `/etc/ntp.conf` (I chose it only because the file name
is short...).


#### Initialization ####

The management of a given file needs to be initialized first with the command:

    $ etcetera --manage /etc/ntp.conf
    SUCCESS: File saved and replaced by symlink


This command will copy the file to a directory managed by etcetera
(`/var/lib/etcetera` by default) and replace `/etc/ntp.conf` with a symlink
to the file.

A few things to note about this command:

* Etcetera will always refuse to execute if it is not invoked with elevated
privileges. One way to do it is to launch a terminal console and login as root
(dangerous and discouraged) to execute Etcetera commands. The other (safe) is
to invoke etcetera through `sudo` as in our example.
* There are abbreviations for all commands. `--manage` can be replaced by `-m`.
Please execute `etcetera --help` for more details.
* All Etcetera commands for which a file name must be provided require a full
path to the file (i.e. starting from the root like `/etc/ntp.conf` and not 
just `ntp.conf`).

> NOTE: Etcetera will only accept to manage files that are located under an
allowed location set in `/etc/etcetera.conf` under `ORIGINAL_LOCATIONS`. By
default, only `/etc` is allowed but more locations can be added.

To verify at any point if the file is managed by etcetera, run:

    $ etcetera --status /etc/ntp.conf
    File was committed on these dates:
        1 | Sat Jan 20 14:43:03 2018 | root root | -rw-r--r-- | (original file)
    File is the same as last commit

This states that the original version of file is now preserved and that the
current version of the file is identical to the preserved version. User, group
and mode is displayed for each version

#### Modifications of the content of file ####

Once the initialization is successful, all operations that are typically
performed on a config file (editing, patching, merging, ...) can be done on
the symlink. for example, if you are moving to Europe you can edit the file
to adjust the first ntp pool:

    $ sudo nano /etc/ntp.conf

add `server europe.pool.ntp.org` as first server entry and save (CTRL+X / Y).

If the status command is executed again, the output is slightly different:

    $ etcetera --status /etc/ntp.conf
    File was committed on these dates:
        1 | Sat Jan 20 14:43:03 2018 | root root | -rw-r--r-- | (original file)
    Some changes to the file are not committed

The last sentence informs that there are now some differences between the
current version of the file and the last preserved version.

#### Preserving the current version of the file ####

To preserve this version of the file to be able to restore it at a later point
in time:

    $ etcetera --commit /etc/ntp.conf --note "Config for Europe"
    SUCCESS: version committed

The `--note` command allows to add a one-line description of what the changes
are about. This parameter is mandatory by default but this requirement can be
disabled by setting `COMMIT_NOTE_REQUIRED = false` in `/etc/etcetera.conf`.

The status command will show what changed:

    $ etcetera --status /etc/ntp.conf
    File was committed on these dates:
        2 | Thu May 17 22:41:04 2018 | root root | -rw-r--r-- | Config for Europe
        1 | Sat Jan 20 14:43:03 2018 | root root | -rw-r--r-- | (original file)
    File is the same as last commit

If the total number of saved files exceeds the maximum permitted
(`COMMIT_MAX_SAVES = 5` by default in `/etc/etcetera.conf`), the oldest
committed version is deleted. The original file is preserved though.

#### Restoring an older version of the file ####

To replace the current version of the file by one that was saved earlier,
in this case the original file, execute:

    $ etcetera --revert /etc/ntp.conf
    File was committed on these dates:
        2 | Thu May 17 22:41:04 2018 | root root | -rw-r--r-- | Config for Europe
        1 | Sat Jan 20 14:43:03 2018 | root root | -rw-r--r-- | (original file)
    Select file version to revert to (1-1, 0 to abort): 1
    SUCCESS: selected version restored

The status command will show:

    $ etcetera --status /etc/ntp.conf
    File was committed on these dates:
        2 | Thu May 17 22:41:04 2018 | root root | -rw-r--r-- | Config for Europe
        1 | Sat Jan 20 14:43:03 2018 | root root | -rw-r--r-- | (original file)
    Some changes to the file are not committed

With the last sentence confirming that the current version (now identical to 
the original file) is different from the content of the last commit (the
configuration with the European server).

#### List files managed by Etcetera ####

    $ etcetera --list
    Files managed by etcetera:
     /etc/ntp.conf
    Number of files managed: 1

#### Stop managing file with Etcetera ####

To return the file to the original location and delete all the commits, run:

    $ etcetera --unmanage /etc/ntp.conf
    SUCCESS: File restored in original location and managed content deleted

The symlink is replaced by the file and if `UNMANAGE_RESTORE_ORIG = true` is
set in `/etc/etcetera.conf` (it is `false` by default) a copy of the original
version of the file is also placed in the original location with the `.orig`
extension. In this case, `/etc/ntp.conf.orig` will appear alongside
`/etc/ntp.conf`.

#### Get some information about the configuration and state of Etcetera ####

Use:

    $ etcetera --info
    Location of config file:
     /etc/etcetera.conf
    Locations where files can be monitored:
     /etc
    Location of managed files:
     /var/lib/etcetera
    Files managed by etcetera:
    Number of files managed: 0
    Max. number of backups preserved for each file: 5
    Original files are preserved: True

> NOTE: The output of this command is preliminary and will change in the future.

### Terminology ###

The folder in which it is allowed to select files for management with Etcetera
is called the **original location** (`/etc` by default). More than one such
folder can be specified in the configuration file of Etcetera.

The file that you have chosen to manage, for example `/etc/ntp.conf` is called
the **original file**.

| Path            | Name              |
|-----------------|-------------------|
| `/etc/`         | Original location |
| `/etc/ntp.conf` | Original file     |

#### After call to --manage ####

Once you have called the *manage* command, The original file is moved to a
directory managed by Etcetera called the **managed location**
(`/var/lib/etcetera` by default). The original file is preserved and a working
copy is created, it is the **Managed File**. The original file is replaced by a
symlink pointing to the managed file.

Every time a successful call to -- manage or --commit is made, a copy of the
managed file is made that is used to detect whether a change has been made to
the managed file that need to be committed. This file is called the **shadow
file** and in our example it is `/var/lib/etcetera/etc/ntp.conf.COMMIT`.

| Path                                    | Name             |
|-----------------------------------------|------------------|
| `/etc/ntp.conf`                         | Symlink          |
| `/var/lib/etcetera`                     | managed location |
| `/var/lib/etcetera/etc/ntp.conf`        | managed file     |
| `/var/lib/etcetera/etc/ntp.conf.ORIG`   | original file    |
| `/var/lib/etcetera/etc/ntp.conf.COMMIT` | shadow file      |

#### After call(s) to --commit ####

Each call to --commit creates a pair of files with an extension including a
timestamp. One is called the **commit file**
(`/var/lib/etcetera/etc/ntp.conf.COMMIT_YYYY-MM-DD_HH-MM-SS`) and the other the
 **comment file** (`/var/lib/etcetera/etc/ntp.conf.COMMENT_YYYY-MM-DD_HH-MM-SS`)

| Path                                                         | Name         |
|--------------------------------------------------------------|--------------|
| `/var/lib/etcetera/etc/ntp.conf.COMMIT_YYYY-MM-DD_HH-MM-SS`  | commit file  |
| `/var/lib/etcetera/etc/ntp.conf.COMMENT_YYYY-MM-DD_HH-MM-SS` | comment file |

All the files in the managed location that share the same base name as the
managed file are called the **associated files** (`*.ORIG`, `*.COMMIT`,
`*.COMMIT_YYYY-MM-DD_HH-MM-SS` and `*.COMMENT_YYYY-MM-DD_HH-MM-SS`).

## Roadmap ##

[roadmap.md](roadmap.md)

## Contributors ##

Jean-Christophe Francois <jc.francois@gmail.com>

## License ##

### GNU General Public License version 3 ###

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


Full terms and conditions are available in the bundled [LICENSE](LICENSE) file.
