# arsa
`arsa.py` is a script for archiving and removing old [Spacewalk](http://www.spacewalkproject.org/), [Red Hat Satellite](http://www.redhat.com/products/enterprise-linux/satellite/) or [SUSE Manager](http://www.suse.com/products/suse-manager/) actions.

The login credentials **are prompted** when running the script. If you need to automate this (*e.g. cronjobs*) you have two options:

## Setting two shell variables
The following shell variables are used:
* **SATELLITE_LOGIN** - a username
* **SATELLITE_PASSWORD** - the appropriate password

You might also want to set the HISTFILE variable (*depending on your shell*) to hide the command including the password in the history:
```
$ HISTFILE="" SATELLITE_LOGIN=mylogin SATELLITE_PASSWORD=mypass ./arsa.py -n
```

## Using an authfile
A better possibility is to create a authfile with permisions **0600**. Just enter the username in the first line and the password in the second line and hand the path to the script:
```
$ ./arsa.py -n -a myauthfile
```

By default the script archives completed actions but you can also remove archived actions.

# Parameters
The following parameters can be specified:

| Parameter | Description |
|:----------|:------------|
| `-d` / `--debug` | enable debugging outputs (*default: no*) |
| `-h` / `--help` | shows help and quits |
| `-a` / `--authfile` | defines an authfile to instead of shell variables |
| `-s` / `--server` | defines the server to use (*default: localhost*) |
| `-r` / `--remove` | archives completed actions and removes all archvied actions (*default: no*) |
| `-n` / `--dry-run` | only lists actions that would be archived (*default: no*) |
| `-f` / `--include-failed` | also include failed actions (*default: no*) |
| `-t` / `--only-system-tasks` | only consider automated system tasks such as package list refresh (*default: no*) |
| `--version` | prints programm version and quits |

# Examples
Listing all completed actions (*login information are passed using shell variables*):
```
$ SATELLITE_LOGIN=mylogin SATELLITE_PASSWORD=mypass ./arsa.py -n
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
