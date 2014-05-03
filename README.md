arsa
====

a script for archiving and removing old Spacewalk, Red Hat Satellite or SUSE Manager actions.

The script requires two shell variables to be set:
* **SATELLITE_LOGIN** - a username
* **SATELLITE_PASSWORD** - the appropriate password

By default the script archives completed actions but you can also remove archived actions.

Parameters
==========

Show internal help:
```
$ ./arsa.py -h
```

Archive completed actions and remove all archived actions afterwards:
```
$ ./arsa.py -r
```

Only list which actions would be deleted (dry-run):
```
$ ./arsa.py -l
```

Specify a different Spacewalk/Red Hat Satellite/SUSE Manager server than **localhost**:
```
$ ./arsa.py -s 192.168.178.100
```

Suppress status outputs:
```
$ ./arsa.py -q
```

Enable debugging outputs for troubleshooting purposes:
```
$ ./arsa.py -d
```

The parameters can also be combined - e.g. doing a dry-run of removing all completed and archived actions:
```
$ ./arsa.py -rl
```

Examples
========

Listing all completed actions:
```
$ ./arsa.py -l
things I'd like to clean (completed):
-------------------------------------
action #1494 ('Remote Command on mymachine.localdomain.loc.')
```

Removing all completed and archived actions:
```
$ ./arsa.py -r
Archving action #1494 ('Remote Command on mymachine.localdomain.loc.')...
Deleting action #1494 ('Remote Command on mymachine.localdomain.loc.')...
Deleting action #1493 ('Remote Command on myothermachine.localdomain.loc.')...
```
