arsa
====

a script for archiving and removing old [Spacewalk](http://www.spacewalkproject.org/), [Red Hat Satellite](http://www.redhat.com/products/enterprise-linux/satellite/) or [SUSE Manager](http://www.suse.com/products/suse-manager/) actions.

The login credentials **are prompted** when running the script. If you need to automate this (*e.g. cronjobs*) you have two options:

**1.Setting two shell variables:**
* **SATELLITE_LOGIN** - a username
* **SATELLITE_PASSWORD** - the appropriate password

You might also want to set the HISTFILE variable (*depending on your shell*) to hide the command including the password in the history:
```
$ HISTFILE="" SATELLITE_LOGIN=mylogin SATELLITE_PASSWORD=mypass ./arsa.py -l
```

**2.Using an authfile**

A better possibility is to create a authfile with permisions 0600. Just enter the username in the first line and the password in the second line and hand the path to the script:
```
$ ./arsa.py -l -a myauthfile
```

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

Only list which actions would be deleted (*dry-run*):
```
$ ./arsa.py -l
```

Archive and remove all actions (*completed, already archived and also failed actions*):
```
$ ./arsa.py -rf
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

Listing all completed actions (*login information are passed using shell variables*):
```
$ SATELLITE_LOGIN=mylogin SATELLITE_PASSWORD=mypass ./arsa.py -l
things I'd like to clean (completed):
-------------------------------------
action #1494 ('Remote Command on mymachine.localdomain.loc.')
```

Removing all completed actions (*login information are provided by the authfile*):
```
$ ./arsa.py -a myauthfile
Archving action #1494 ('Remote Command on mymachine.localdomain.loc.')...
```

Removing all completed and archived actions (*login information are prompted*):
```
$ ./arsa.py -r
Username: mylogin
Password: 
Archving action #1494 ('Remote Command on mymachine.localdomain.loc.')...
Deleting action #1494 ('Remote Command on mymachine.localdomain.loc.')...
Deleting action #1493 ('Remote Command on myothermachine.localdomain.loc.')...
```
