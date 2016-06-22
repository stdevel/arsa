#!/usr/bin/python

# arsa.py - a script for archiving and removing old
# Spacewalk, Red Hat Satellite or SUSE Manager actions.
#
# 2016 By Christian Stankowic
# <info at stankowic hyphen development dot net>
# https://github.com/stdevel
#

from optparse import OptionParser, OptionGroup
import xmlrpclib
import os
import stat
import getpass
import time

#list of supported API levels
supportedAPI = ["11.1","12","13","13.0","14","14.0","15","15.0","16","16.0","17","17.0"]

if __name__ == "__main__":
        #define description, version and load parser
        desc='''%prog is used to archive completed actions and remove archived actions on Spacewalk, Red Hat Satellite and SUSE Manager. Login credentials are assigned using the following shell variables:

                SATELLITE_LOGIN  username
                SATELLITE_PASSWORD  password

                It is also possible to create an authfile (permissions 0600) for usage with this script. The first line needs to contain the username, the second line should consist of the appropriate password.
If you're not defining variables or an authfile you will be prompted to enter your login information.

                Checkout the GitHub page for updates: https://github.com/stdevel/arsa'''
        parser = OptionParser(description=desc,version="%prog version 0.4")
	
	#define option groups
	genOpts = OptionGroup(parser, "Generic Options")
	satOpts = OptionGroup(parser, "Satellite Options")
	parser.add_option_group(genOpts)
	parser.add_option_group(satOpts)
	
        #-a / --authfile
        satOpts.add_option("-a", "--authfile", dest="authfile", metavar="FILE", default="", help="defines an auth file to use instead of shell variables")

        #-s / --server
        satOpts.add_option("-s", "--server", dest="server", metavar="SERVER", default="localhost", help="defines the server to use (default: localhost)")

        #-q / --quiet
        genOpts.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout (default: no)")

        #-d / --debug
        genOpts.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="enable debugging outputs (default: no)")

        #-r / --remove
        satOpts.add_option("-r", "--remove", dest="remove_all", default=False, action="store_true", help="archives completed actions and removes all archived actions (default: no)")

        #-n / --dry-run
        satOpts.add_option("-n", "--dry-run", dest="dry_run", default=False, action="store_true", help="only lists actions that would be archived (default: no)")

        #-f / --include-failed
        satOpts.add_option("-f", "--include-failed", dest="include_failed", default=False, action="store_true", help="also include failed actions (default: no)")

        #-t / --system-tasks
        satOpts.add_option("-t", "--only-system-tasks", dest="only_system_tasks", default=False, action="store_true", help="only consider automated system tasks such as package list refresh (default: no)")

        #parse arguments
        (options, args) = parser.parse_args()

        #define URL and login information
        SATELLITE_URL = "http://"+options.server+"/rpc/api"

        #setup client and key depending on mode
        client = xmlrpclib.Server(SATELLITE_URL, verbose=options.debug)
        if options.authfile:
                #use authfile
                if options.debug: print "DEBUG: using authfile"
                try:
                        #check filemode and read file
                        filemode = oct(stat.S_IMODE(os.lstat(options.authfile).st_mode))
                        if filemode == "0600":
                                if options.debug: print "DEBUG: file permission ("+filemode+") matches 0600"
                                fo = open(options.authfile, "r")
                                s_username=fo.readline().replace("\n", "")
                                s_password=fo.readline().replace("\n", "")
                                key = client.auth.login(s_username, s_password)
                        else:
                                if options.verbose: print "ERROR: file permission ("+filemode+") not matching 0600!"
                                exit(1)
                except OSError:
                        print "ERROR: file non-existent or permissions not 0600!"
                        exit(1)
        elif "SATELLITE_LOGIN" in os.environ and "SATELLITE_PASSWORD" in os.environ:
                #shell variables
                if options.debug: print "DEBUG: checking shell variables"
                key = client.auth.login(os.environ["SATELLITE_LOGIN"], os.environ["SATELLITE_PASSWORD"])
        else:
                #prompt user
                if options.debug: print "DEBUG: prompting for login credentials"
                s_username = raw_input("Username: ")
                s_password = getpass.getpass("Password: ")
                key = client.auth.login(s_username, s_password)

        #check whether the API version matches the minimum required
        api_level = client.api.getVersion()
        if not api_level in supportedAPI:
                print "ERROR: Your API version ("+api_level+") does not support the required calls. You'll need API version 1.8 (11.1) or higher!"
                exit(1)
        else:
                if options.debug: print "INFO: supported API version ("+api_level+") found."

        #retrieve completed, already archived and failed actions
        toArchive = []
        completed_actions = client.schedule.listCompletedActions(key)
        archived_actions = client.schedule.listArchivedActions(key)
        failed_actions = client.schedule.listFailedActions(key)

        #what to consider as a system task
        systemTasks = [ 'Show differences between', 'Activation Key Package Auto-Install', 'Package List Refresh', 'Hardware List Refresh' ]

        #print actions
        if options.debug: print "completed:\n"+`completed_actions`+"\narchived:\n"+`archived_actions`

        #go through completed actions and remove them if wanted
        if options.dry_run: print "things I'd like to clean (completed):\n-------------------------------------"
        for entry in completed_actions:
            if options.only_system_tasks:
                for task in systemTasks:
                    if task in entry["name"]:
                        if options.verbose: print "Found completed system task action #"+`entry["id"]`+" ("+`entry["name"]`+")..."
                        toArchive.append(entry["id"])
            else:
                if options.verbose: print "Found completed action #"+`entry["id"]`+" ("+`entry["name"]`+")..."
                toArchive.append(entry["id"])

        #also clean-up already archived actions if wanted
        if options.remove_all:
                #remove archived actions
                if options.dry_run: print "\nthings I'd like to remove (archived):\n-------------------------------------"
                for entry in archived_actions:
                    if options.only_system_tasks:
                        for task in systemTasks:
                            if task in entry["name"]:
                                if options.verbose: print "Found archived system task action #"+`entry["id"]`+" ("+`entry["name"]`+")..."
                                toArchive.append(entry["id"])
                    else:
                        if options.verbose: print "Found archived action #"+`entry["id"]`+" ("+`entry["name"]`+")..."
                        toArchive.append(entry["id"])

        #also clean-up failed actions if wanted
        if options.include_failed:
                #remove failed actions
                if options.dry_run: print "\nthings I'd like to remove (failed):\n-----------------------------------"
                for entry in failed_actions:
                    if options.only_system_tasks:
                        for task in systemTasks:
                            if task in entry["name"]:
                                if options.verbose: print "Found failed system task action #"+`entry["id"]`+" ("+`entry["name"]`+")..."
                                toArchive.append(entry["id"])
                    else:
                        if options.verbose: print "Found failed action #"+`entry["id"]`+" ("+`entry["name"]`+")..."
                        toArchive.append(entry["id"])

        #archive (and remove) actions if wanted
        if options.debug: print "\nINFO: toArchive:" + str(`toArchive`)

        #removing duplicate entries
        toArchive = list(set(toArchive))
	
	#remove actions if dry_run not set
	if options.dry_run == False:
        	if options.verbose: print "Archiving actions..."
        	#enable 100 actions-per-call workaround if we dug hundreds actions
	        if len(toArchive) > 100:
	                if options.verbose: print "Enabling workaround to archive/delete more than 100 actions..."
	                tempActions = []
	                for action in toArchive:
	                        if len(tempActions) != 100:
	                                tempActions.append(action)
	                        else:
	                                print tempActions
	                                client.schedule.archiveActions(key,tempActions)
	                                time.sleep(.5)
	                                if options.remove_all:
	                                        client.schedule.deleteActions(key,tempActions)
	                                        time.sleep(.5)
	                                tempActions = []
	        else:
	                client.schedule.archiveActions(key,toArchive)
	                if options.remove_all:
				client.schedule.deleteActions(key,toArchive)
	else:
		if options.verbose: print "Stopping here as we don't really want to remove actions..."
	
        #logout and exit
        client.auth.logout(key)
