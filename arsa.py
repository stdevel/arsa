#!/usr/bin/python

# arsa.py - a script for archiving and removing old
# Spacewalk, Red Hat Satellite or SUSE Manager actions.
#
# 2014 By Christian Stankowic
# <info at stankowic hyphen development dot net>
# https://github.com/stdevel
#

from optparse import OptionParser
import xmlrpclib
import os

#list of supported API levels
supportedAPI = ["11.1","12","13","14"]

if __name__ == "__main__":
        #define description, version and load parser
        desc='''%prog is used to archive completed actions and remove archived actions on Spacewalk, Red Hat Satellite and SUSE Manager.
                Login credentials are assigned using the following shell variables:
                SATELLITE_LOGIN  username
                SATELLITE_PASSWORD  password
                Make sure to export or assign these variables before running the script!

                Checkout the GitHub page for updates: https://github.com/stdevel/arsa'''
        parser = OptionParser(description=desc,version="%prog version 0.1")

        #-s / --server
        parser.add_option("-s", "--server", dest="server", metavar="SERVER", default="localhost", help="defines the server to use")

        #-q / --quiet
        parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")

        #-d / --debug
        parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="enable debugging outputs")

        #-r / --remove
        parser.add_option("-r", "--remove", dest="removeAll", default=False, action="store_true", help="archives completed actions and removes all archived actions")

        #-l / --list-only
        parser.add_option("-l", "--list-only", dest="listonly", default=False, action="store_true", help="only lists actions that would be archived")

        #parse arguments
        (options, args) = parser.parse_args()

        #check whether the satellite shell variables are given
        if not "SATELLITE_LOGIN" in os.environ or not "SATELLITE_PASSWORD" in os.environ:
                print "ERROR: you need to specify the SATELLITE_LOGIN and SATELLITE_PASSWORD shell variables!"
                exit(1)
        else:
                #define URL and login information
                SATELLITE_URL = "http://"+options.server+"/rpc/api"

                #setup client and key
                client = xmlrpclib.Server(SATELLITE_URL, verbose=options.debug)
                key = client.auth.login(os.environ["SATELLITE_LOGIN"], os.environ["SATELLITE_PASSWORD"])

                #check whether the API version matches the minimum required
                api_level = client.api.getVersion()
                if not api_level in supportedAPI:
                        print "ERROR: your API version ("+api_level+") does not support the required calls. You'll need API version 1.8 (11.1) or higher!"
                        exit(1)
                else:
                        if options.debug: print "INFO: supported API version ("+api_level+") found."

                #retrieve completed and already archived actions
                completed_actions = client.schedule.listCompletedActions(key)
                archived_actions = client.schedule.listArchivedActions(key)

                #print actions
                if options.debug: print "completed:\n"+`completed_actions`+"\narchived:\n"+`archived_actions`

                #go through completed actions and remove them if wanted
                if options.listonly: print "things I'd like to clean (completed):\n-------------------------------------"
                for entry in completed_actions:
                        if options.listonly:
                                print "action #"+`entry["id"]`+" ("+`entry["name"]`+")"
                        else:
                                #archive actions
                                if options.verbose: print "Archving action #"+`entry["id"]`+" ("+`entry["name"]`+")..."
                                client.schedule.archiveActions(key,entry["id"])

                #also clean-up already archived actions if wanted
                if options.removeAll:
                        if options.listonly: print "\nthings I'd like to remove (archived):\n-------------------------------------"
                        for entry in archived_actions:
                                if options.listonly:
                                        print "action #"+`entry["id"]`+" ("+`entry["name"]`+")"
                                else:
                                        if options.verbose: print "Deleting action #"+`entry["id"]`+" ("+`entry["name"]`+")..."
                                        client.schedule.deleteActions(key,entry["id"])
