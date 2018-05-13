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
* Handle option to restore .orig file along with shadow file

**DONE**

### --list ###

List all files currently managed by etcetera

**DONE**

## Version 0.2 ##

### Split etcetera_mod.py in `commands.py` and `functions.py` ###

**DONE**

### Add functions in toolbox ###

**DONE**

### --manage FILENAME ###

* Add .COMMIT version of the file

**DONE***

### --commit FILENAME ###

* Verify that there are differences between file and its .COMMIT (toolbox function)
* If there aren't, tell the user
* If there are, save copy of file under `.COMMIT` and `.COMMIT[timestamp]`
* Count the number of `.COMMIT[timestamp]` files present. If there are more than allowed delete the oldest.

**DONE**

### --revert FILENAME ###

* Propose list to pick from
* Overwrite managed file with the chosen .COMMIT version

**DONE**

### --status FILENAME ###

* Check that symlink points to file with same name in shadow location
* Mention if there are uncommitted changes to file
* Mention if .ORIG file is available
* List .COMMIT and .ORIG files

**DONE**

### --info ###

Provide useful information about etcetera configuration and state.

* Location of configuration file
* Original locations being monitored
* Location of shadow directory
* Number of managed files
* Max number of backups preserved for each file
* Whether `.ORIG` files are preserved

**DONE**

## Version 0.3 ##

### --commit FILENAME COMMENT ###

Capture and save a comment string to display when showing list of commits

**DONE**

### --revert FILENAME ###

* Display comment alongside list of available commits to revert

**DONE**

### --status FILENAME ###

* Display comment alongside list of available commits to revert

**DONE**

## Version 0.4 ##

### Flag that a file has changed even if only mode/owner/group has changed ###

**DONE**

### Clarify vocabulary ###

* manage/unmanage
* original/shadow
* rev/revert

**DONE**

### Write initial documentation ###

**DONE**

### Write (un)install.sh ###

**DONE**

### Remote on github ###

**DONE**

## Version 0.5 ##

### Reverse order of list of commits ###

So that older commits always keep the same order number (original file = 1)

**DONE**

### gain elevated privileges if not already available

To avoid having to type `sudo` at every invocation

**DONE**

## Later ##

### Colored output ###

### display user/group/mode in commit list

### --manage FILENAME ###

Support specifying directories instead of individual files (e.g. `/etc/ssh`)

### --unmanage FILENAME ###

* Support specifying directories instead of individual files (e.g. `/etc/ssh`)

### Monitor file changes ###

Use pyinotify module to monitor file changes and auto-commit

### Logging to journal ###

Log to systemd journal using systemd.journal python module

### implement doctest ###

Start with toolbox functions

### Option to keep or delete shadow files after call to --unmanage ####

    # Delete all shadow files after restoration into original location when calling --unmanage (true/false)
    Default is false
    KEEP_SHADOWS_AFTER_UNMANAGE = false

It may be difficult to handle a subsequent call to --manage. What to do with .ORIG?

### Confirmation option for destructive changes ###

Are you sure (y/N) for:

* --revert if uncommitted changes exist in file
* --unmanage

### Security check ###

Avoid that a rogue file is introduced as a replacement for a config file

### possibility to commit files with relative path ###

* pass the symlink argument to function that returns the full path

### Hardening ###

#### Avoid config file breakage ####

Access and verify config file variable at the beginning of the execution of a command
to avoid failing midway due to a typo in the config file

#### Disallow saving in some locations ####

    /proc
    /bin

#### Ensure consistency of repository ####

* Verify that no symlinks are dead
* Handle case where a location has been removed from MANAGED_LOCATIONS

### Review command-line parameters syntax ###

* Implement FILENAME with parent (?)

### Revise output of --info ###

