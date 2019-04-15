#!/usr/bin/python

# *******************************************************************************
# Name: d9_aws_acct_add.py
# Description: A simple Dome9 script to automate the addition of an AWS account
# to a Dome9 account - including the AWS dependencies via CloudFormation template
# Author: Patrick Pushor
# todo : lambda-ize and package this via ?, add more error handling and logging
#
# Copywrite 2018, Dome9 Security
# www.dome9.com - secure your cloud
# *******************************************************************************

import json
import time
import sys
import configparser
import requests
import string
from random import *
from time import sleep
from requests.auth import HTTPBasicAuth
from datetime import datetime

def run():
    print ("Starting Dome9 AWS Account Add Script...")
    start = datetime.utcnow()

    # load config file
    config = configparser.ConfigParser()
    config.read("./d9_aws_acct_add.conf")

    # set up our Dome9 API endpoint(s) and other Dome9 dependencies
    d9id = config.get('dome9', 'd9id')
    d9secret = config.get('dome9','d9secret')
    d9mode = config.get('dome9','d9mode')
    externalid = config.get('dome9','externalid')
    url = "https://api.dome9.com/v2/CloudAccounts"

    if d9id and d9secret and d9mode and externalid != "":
        print ('Configuration file values found.')
    else:
        print ('Please ensure that all config settings in d9_aws_acct_add.conf are set.')
        sys.exit()

    if d9mode == ('readonly'):
        d9readonly = ('true')
    elif d9mode == ('readwrite'):
        d9readonly = ('false')
    else:
        print ('Set the Dome9 account mode (readonly vs readwrite) in the config file...')
        sys.exit()

    # Make the API call to Dome9
    urldata = {"name": sys.argv[1], "credentials": {"arn": sys.argv[2], "secret": externalid, "type": "RoleBased", "isReadOnly": d9readonly}, "fullProtection": "false"}
    headers = {'content-type': 'application/json'}

    print('Calling the Dome9 API with all required info to add your AWS account.')

    resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
    print (resp.content)

if __name__ == '__main__': run()
