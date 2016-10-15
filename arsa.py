#!/usr/bin/env python
# -*- coding: utf-8 -*-

# arsa.py - a script for archiving and removing old
# Spacewalk, Red Hat Satellite 5.x or SUSE Manager actions.
#
# 2016 By Christian Stankowic
# <info at stankowic hyphen development dot net>
# https://github.com/stdevel
#

from optparse import OptionParser, OptionGroup
import logging
import xmlrpclib
import os
import stat
import getpass
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

#set logger
LOGGER = logging.getLogger('arsa.py')

#list of supported API levels
supported_api = ["11.1","12","13","13.0","14","14.0","15","15.0","16","16.0","17","17.0"]

def clean_actions():
	#clean _all_ the actions
	
        #setup client and key depending on mode
        client = xmlrpclib.Server(satellite_url, verbose=options.debug)
        if options.authfile:
                #use authfile
		LOGGER.debug("Using authfile")
                try:
                        #check filemode and read file
                        filemode = oct(stat.S_IMODE(os.lstat(options.authfile).st_mode))
                        if filemode == "0600":
                                LOGGER.debug("File permission ({0}) matches 0600".format(filemode))
                                fo = open(options.authfile, "r")
                                s_username=fo.readline().replace("\n", "")
                                s_password=fo.readline().replace("\n", "")
                                key = client.auth.login(s_username, s_password)
                        else:
                                LOGGER.error("File permission ({0}) not matching 0600!".format(filemode))
                                exit(1)
                except OSError:
			LOGGER.error("File non-existent or permissions not 0600!")
                        exit(1)
        elif "SATELLITE_LOGIN" in os.environ and "SATELLITE_PASSWORD" in os.environ:
                #shell variables
		LOGGER.debug("Checking shell variables")
                key = client.auth.login(os.environ["SATELLITE_LOGIN"], os.environ["SATELLITE_PASSWORD"])
        else:
                #prompt user
                LOGGER.debug("Prompting for login credentials")
                s_username = raw_input("Username: ")
                s_password = getpass.getpass("Password: ")
                key = client.auth.login(s_username, s_password)

        #check whether the API version matches the minimum required
        api_level = client.api.getVersion()
        if not api_level in supported_api:
		LOGGER.error("Your API version ({0}) does not support the needed calls. You need API version 1.8 (11.1) or higher!".format(api_level))
                exit(1)
        else:
		LOGGER.debug("Supported API version ({0}) fround".format(api_level))

        #retrieve completed, already archived and failed actions
        to_archive = []
        completed_actions = client.schedule.listCompletedActions(key)
        archived_actions = client.schedule.listArchivedActions(key)
        failed_actions = client.schedule.listFailedActions(key)

        #what to consider as a system task
        system_tasks = [ 'Show differences between', 'Activation Key Package Auto-Install', 'Package List Refresh', 'Hardware List Refresh' ]

        #print actions
	LOGGER.debug("Completed:\n{0}Archived:\n{1}".format(completed_actions, archived_actions))

        #go through completed actions and remove them if wanted
	if options.dry_run: LOGGER.info("Things I'd like to clean (completed):\n")
        for entry in completed_actions:
            if options.only_system_tasks:
                for task in system_tasks:
                    if task in entry["name"]:
			LOGGER.info("Found completed system task action #{0} ({1})...".format(entry['id'], entry['name']))
                        to_archive.append(entry["id"])
            else:
		LOGGER.info("Found completed action #{0} ({1})...".format(entry['id'], entry['name']))
                to_archive.append(entry["id"])

        #also clean-up already archived actions if wanted
        if options.remove_all:
                #remove archived actions
		if options.dry_run: LOGGER.info("Things I'd like to remove (archived):\n")
                for entry in archived_actions:
                    if options.only_system_tasks:
                        for task in system_tasks:
                            if task in entry["name"]:
				LOGGER.info("Found archived system task action #{0} ({1})...".format(entry['id'], entry['name']))
                                to_archive.append(entry["id"])
                    else:
			LOGGER.info("Found archvied action #{0} ({1})...".format(entry['id'], entry['name']))
                        to_archive.append(entry["id"])

        #also clean-up failed actions if wanted
        if options.include_failed:
                #remove failed actions
		if options.dry_run: LOGGER.info("Things I'd like to remove (failed):\n")
                for entry in failed_actions:
                    if options.only_system_tasks:
                        for task in system_tasks:
                            if task in entry["name"]:
				LOGGER.info("Found failed system task action #{0} ({1})...".format(entry['id'], entry['name']))
                                to_archive.append(entry["id"])
                    else:
			LOGGER.info("Found failed action #{0} ({1})...".format(entry['id'], entry['name']))
                        to_archive.append(entry["id"])

        #archive (and remove) actions if wanted
	LOGGER.debug("\nto_archive: {0}".format(str(to_archive)))
	
        #removing duplicate entries
        to_archive = list(set(to_archive))
	
	#remove actions if dry_run not set
	if options.dry_run == False:
		LOGGER.info("Archiving actions...")
        	#enable 100 actions-per-call workaround if we found hundreds of actions
	        if len(to_archive) > 100:
			LOGGER.debug("Enabling workaround to archive/delete 100+ actions...")
	                temp_actions = []
	                for action in to_archive:
	                        if len(temp_actions) != 100:
	                                temp_actions.append(action)
	                        else:
					LOGGER.debug("Removing actions: {0}".format(str(temp_actions)))
	                                client.schedule.archiveActions(key,temp_actions)
	                                time.sleep(.5)
	                                if options.remove_all:
	                                        client.schedule.deleteActions(key,temp_actions)
	                                        time.sleep(.5)
	                                temp_actions = []
	        else:
	                client.schedule.archiveActions(key,to_archive)
	                if options.remove_all:
				client.schedule.deleteActions(key,to_archive)
	else:
		LOGGER.info("Stopping here as we don't really want to clean things up")
	
        #logout and exit
        client.auth.logout(key)

if __name__ == "__main__":
        #define description, version and load parser
        desc='''%prog is used to archive completed actions and remove archived actions on Spacewalk, Red Hat Satellite 5.x and SUSE Manager. Login credentials are assigned using the following shell variables:

                SATELLITE_LOGIN  username
                SATELLITE_PASSWORD  password

                It is also possible to create an authfile (permissions 0600) for usage with this script. The first line needs to contain the username, the second line should consist of the appropriate password.
If you're not defining variables or an authfile you will be prompted to enter your login information.

                Checkout the GitHub page for updates: https://github.com/stdevel/arsa'''
        parser = OptionParser(description=desc,version="%prog version 0.4.1")
	
	#define option groups
	gen_opts = OptionGroup(parser, "Generic Options")
	sat_opts = OptionGroup(parser, "Satellite Options")
	parser.add_option_group(gen_opts)
	parser.add_option_group(sat_opts)
	
        #-a / --authfile
        sat_opts.add_option("-a", "--authfile", dest="authfile", metavar="FILE", default="", help="defines an auth file to use instead of shell variables")

        #-s / --server
        sat_opts.add_option("-s", "--server", dest="server", metavar="SERVER", default="localhost", help="defines the server to use (default: localhost)")

        #-d / --debug
        gen_opts.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="enable debugging outputs (default: no)")

        #-r / --remove
        sat_opts.add_option("-r", "--remove", dest="remove_all", default=False, action="store_true", help="archives completed actions and removes all archived actions (default: no)")

        #-n / --dry-run
        sat_opts.add_option("-n", "--dry-run", dest="dry_run", default=False, action="store_true", help="only lists actions that would be archived (default: no)")

        #-f / --include-failed
        sat_opts.add_option("-f", "--include-failed", dest="include_failed", default=False, action="store_true", help="also include failed actions (default: no)")

        #-t / --system-tasks
        sat_opts.add_option("-t", "--only-system-tasks", dest="only_system_tasks", default=False, action="store_true", help="only consider automated system tasks such as package list refresh (default: no)")

        #parse arguments
        (options, args) = parser.parse_args()

        #define URL and login information
        satellite_url = "http://"+options.server+"/rpc/api"
	
	#set logger level
	if options.debug:
		logging.basicConfig(level=logging.DEBUG)
		LOGGER.setLevel(logging.DEBUG)
	else:
		logging.basicConfig()
	LOGGER.setLevel(logging.INFO)
	
	#clean actions
	clean_actions()
