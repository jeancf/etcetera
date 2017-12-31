# Roadmap for etcetera #

## Version 0.1 ##

This version is not functional yet. It does not save copies of the config file every time it is saved.

### --manage FILENAME ###

Take over file for tracking.

* Verify that file is valid
* Copy file over to shadow directory
* Replace file in original location by a symlink to the file in shadow directory
* Save copy of file with .etc_orig extension

**DONE**

### --unmanage FILENAME ###

Reinstate file in its original location.

* Replace symlink in original location by file from shadow directory
* Delete all related files in the shadow directory
* Delete empty directories in the path within the shadow directory

### --list ###

List all files currently managed by etcetera

## Version 0.2 ##

### --manage FILENAME ###

Support specifying directories instead of individual files (e.g. `/etc/ssh`)

### --unmanage FILENAME ###

* Support specifying directories instead of individual files (e.g. `/etc/ssh`)
* Handle option to restore .orig file along with shadow file

### --rev FILENAME ###

Increment version of file by taking a backup of the previous version (the one when --manage or --rev was called last).
Can be invoked before or after modification of file.

### --rollback FILENAME ###

Discard all changes made since --manage or --rev was called last.

### --info ###

Provide useful information about etcetera configuration and state

* Number of managed files
* Original locations being monitored
* Location of shadow directory
* Max number of backups preserved for each file
* Whether `.orig` files are preserved
* Location of configuration file

### logging to journal ###

Log to systemd journal using systemd.journal python module

### Colored output ###

## Later ##

### ensure consistency of repository ### 

* Verify that no symlinks are dead
* Handle case where a location has been removed from MANAGED_LOCATIONS

### Monitor file changes ###

Use pyinotify module to monitor file changes and rev

### Automate testing ###