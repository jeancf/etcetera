#!/bin/bash

#    Copyright (C) 2018  Jean-Christophe Francois
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


do_install()
{
    # Create directories
    if [ ! -d /var/lib/etcetera ]; then
        mkdir /var/lib/etcetera
    fi

    if [ ! -d /usr/share/etcetera ]; then
        mkdir /usr/share/etcetera
    fi

    if [ ! -d /usr/lib/etcetera ]; then
        mkdir /usr/lib/etcetera
    fi

    # Copy files and set mode

    # If etcetera.conf already exist install under .new instead
    if [ ! -e /etc/etcetera.conf ]; then
        cp etcetera.conf /etc/
        chown root:root /etc/etcetera.conf
        chmod 640 /etc/etcetera.conf
    else
        cp etcetera.conf /etc/etcetera.conf.new
        chown root:root /etc/etcetera.conf.new
        chmod 640 /etc/etcetera.conf.new
    fi

    cp README.md /usr/share/etcetera
    chown root:root /usr/share/etcetera/README.md
    chmod 640 /usr/share/etcetera/README.md

    cp etcetera-logo.png /usr/share/etcetera
    chown root:root /usr/share/etcetera/etcetera-logo.png
    chmod 640 /usr/share/etcetera/etcetera-logo.png

    cp install-etcetera.sh /usr/share/etcetera

    cp parser.py /usr/lib/etcetera
    chown root:root /usr/lib/etcetera/parser.py
    chmod 755 /usr/lib/etcetera/parser.py

    cp commands.py /usr/lib/etcetera
    chown root:root /usr/lib/etcetera/commands.py
    chmod 640 /usr/lib/etcetera/commands.py

    cp toolbox.py /usr/lib/etcetera
    chown root:root /usr/lib/etcetera/toolbox.py
    chmod 640 /usr/lib/etcetera/toolbox.py

    cp term_colors.py /usr/lib/etcetera
    chown root:root /usr/lib/etcetera/term_colors.py
    chmod 640 /usr/lib/etcetera/term_colors.py

    cp etcetera /usr/bin
    chown root:root /usr/bin/etcetera
    chmod 755 /usr/bin/etcetera

    echo "Installation done."
}


do_remove()
{
    echo "This will remove etcetera from this computer, please confirm (y/N): "
    read CONFIRM

    if [ "$CONFIRM" != "y" ]; then
        echo "Aborted."
        exit 1
    fi

    # Remove /usr/share/etcetera
    rm /usr/share/etcetera/ -r

    # Remove files from /usr/lib/etcetera and directory if empty
    rm /usr/lib/etcetera/parser.py
    rm /usr/lib/etcetera/commands.py
    rm /usr/lib/etcetera/toolbox.py
    rm /usr/lib/etcetera/term_colors.py

    if [ -d /usr/lib/etcetera/__pycache__ ]; then
        rm /usr/lib/etcetera/__pycache__ -r
    fi

    if [ "`find /usr/lib/etcetera -type d -empty`" = "/usr/lib/etcetera" ]; then
        rmdir /usr/lib/etcetera
    fi

    # Remove /var/lib/etcetera only if it is empty
    if [ "`find /var/lib/etcetera -type d -empty`" = "/var/lib/etcetera" ]; then
        rmdir /var/lib/etcetera
    fi

    # Remove file from /usr/bin
    rm /usr/bin/etcetera

    echo "etcetera removed from system."
}

#### Execution starts here ####

# Verify that user has root privilege
if [ ! $UID -eq 0 ]; then
    echo "ERROR: install.sh must be executed with elevated privileges. try sudo ./install.sh"
    exit 1
fi

# Process command line parameters
if [ "$1" = "--remove" ]; then
    do_remove;
else
    do_install;
fi