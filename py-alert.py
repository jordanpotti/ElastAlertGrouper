#!/usr/bin/python

import sys
from argparse import ArgumentParser
import datetime
import requests
import subprocess
import os

time = datetime.datetime.fromtimestamp(1514903262).isoformat()


def print_banner():
    print('''\npy-alert.py is a tool written to expand the functionality of ElastAlert
    Author: Jordan Potti
    Twitter: @ok_bye_now\n'''
    )

def main():
    global arguments
    parser = ArgumentParser()
    parser.add_argument("-T", dest="action",required=False,help="Action Type: Send Alert (S) or Data Write (D)")
    parser.add_argument("-a", dest="detection",required=False,help="Alert Name")
    parser.add_argument("-o", dest="outfile",required=False,help="Output file name")
    parser.add_argument("-c", dest="host",required=False,help="Host to record")
    parser.add_argument("-S", dest="slack",required=False,help="Slack Web Hook")
    parser.add_argument("-t", dest="tripped",required=False,help="Number or Hosts needed to alert")

    if len(sys.argv) == 1:
        print_banner()
        parser.error("No arguments given.")
        parser.print_usage
        sys.exit()

    arguments = parser.parse_args()
    
    if arguments.action == 'D':
        with open (arguments.outfile, "a+") as out_file:
            out_file.write(arguments.host+"\n")
            #out_file.write("Alert Type: " + arguments.detection+"\n")
            #out_file.write("Time: " + time)

    if arguments.action == 'S':
        command = "sort /tmp/mimikatz | uniq -c | gawk '$1>=%s{print $2}'" %arguments.tripped
        #print(command)
        #output = os.popen("sort /tmp/mimikatz | uniq -c | gawk '$1>=5{print $2}'").read()
        output = os.popen(command).read()
        if output != '':
            output = str(output)
            output = output.replace('b\'','')
            output = output.replace('\\n','')
            out_file = open(arguments.outfile, 'w')
            out_file.write("Host: " + output)
            out_file.write("Alert Type: " + arguments.detection+"\n")
            out_file.write("Time: " + time)
        #try: 
        #out_file.close()
        out_file = open(arguments.outfile, 'r')
        webhook_url = arguments.slack
        slack_data = {"text":out_file.read()}
        slack_data = str(slack_data)
        slack_data = "payload="+slack_data
        response = requests.post(
            webhook_url, data=slack_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if response.status_code != 200:
            raise ValueError('Request to slack returned an error %s, the response is: %s' % (response.status_code, response.text))
        #except:
        #    print("Error")
        os.remove(arguments.outfile)

main()
