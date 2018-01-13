Etcetera
========

![etcetera-logo.png](etcetera-logo.png)

**Config file management with a touch of wisdom.**

## About ##

Etcetera is a simple command line tool that lets you keep track of the changes
to config files of a linux system.
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

* Strictly define locations where files can be managed by etc
* Select which files to manage
* Commit changes to a managed file with associated note
* Revert changes by selecting a previous commit
* Restore managed file back to the original location

## Download and install ##

### Archlinux ###

The `etcetera` package is available in the AUR.

### Manual installation ###

Clone the project or download and unpack the zip file from github.

Copy project files to the following locations on your system:

| File            | Location                      | Mode |
|-----------------|-------------------------------|------|
| `etcetera`      | `/usr/bin`                    | 755  |
| `commands.py`   | `/usr/share/etcetera`         | 644  |
| `toolbox.py`    | `/usr/share/etcetera`         | 644  |
| `etcetera.conf` | `/etc/etcetera/etcetera.conf` | 644  |

Make sure they are all owned by `root:root`,  including the directories
`/usr/share/etcetera` and `/etc/etcetera`  and that they have the correct mode
set.

## Documentation ##

### Getting Started ###

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
