#!/usr/bin/env python

import json
import os
import sys
from time import sleep
import argparse
import configparser
import requests
import random, string
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from datetime import datetime

d9id = ''
d9secret = ''
cloudid = ''

def add_aws_account(name, arn, extid):

    url = "https://api.dome9.com/v2/CloudAccounts"
    urldata = {"name": name, "credentials": {"arn": arn, "secret": extid, "type": "RoleBased", "isReadOnly": "true"}, "fullProtection": "false"}
    headers = {'content-type': 'application/json'}

    print('Calling the Dome9 API with all required info to add AWS account.')

    resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
    
    if resp.status_code == 201:
        resp = json.loads(resp.content)
        print('AWS account added successfully, id: ' + resp['id'])
        return resp['id']
    
    elif resp.status_code == 400:
        print('AWS Cloud Account already added. Please remove from Dome9 before using this script.')

    else:
        print('Error when attempting to add AWS account.')
        print(resp)
        return False
        
def add_notification_policy(name, email):

    url = "https://api.dome9.com/v2/Compliance/ContinuousComplianceNotification"
    urldata = {"name":name,"description":"","alertsConsole":False,"scheduledReport":{"emailSendingState":"Disabled"},"changeDetection":{"emailSendingState":"Enabled","emailPerFindingSendingState":"Disabled","snsSendingState":"Disabled","externalTicketCreatingState":"Disabled","awsSecurityHubIntegrationState":"Disabled","emailData":{"recipients":[email]}},"gcpSecurityCommandCenterIntegration":{"state":"Disabled"}}
    headers = {'content-type': 'application/json'}
    print('Creating Notification Policy')
    
    resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)

    if resp.status_code == 201:
        resp = json.loads(resp.content)
        print('Dome9 Notification policy added successfully. name: ' + name + ', id: ' + resp['id'])
        return resp['id']
    
    elif resp.status_code == 400:
        print('Dome9 Notification policy bad request.')
        print('resp')

    else:
        print('Error when attempting to add Notification policy.')
        print(resp)
        return False
        
def add_cc_policy(d9cloudaccountid, extaccountid, notificationid, rulesetid):

    url = "https://api.dome9.com/v2/Compliance/ContinuousCompliancePolicy/ContinuousCompliancePolicies"
    urldata = [{"cloudAccountId":d9cloudaccountid,"bundleId":rulesetid,"externalAccountId":extaccountid,"cloudAccountType":cloudid,"notificationIds":[notificationid],"product":"compliance"}]
    headers = {'content-type': 'application/json'}
    print('Creating Continuous Compliance Policy')

    try:
        resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
        
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}') 
    else:
        print('Success!')

    if resp.status_code == 201:
        resp = json.loads(resp.content)
        print('Dome9 Continuous Compliance policy added successfully. id: ' + resp[0]['id'])
        return resp[0]['id']
    
    elif resp.status_code == 400:
        print('Dome9 Continuous Compliance policy bad request.')
        print(resp)

    else:
        print('Error when attempting to add Continuous Compliance policy.')
        print(resp)
        return False

def send_all_alerts(notificationpolicyid, compliancepolicyid):

    url = 'https://api.dome9.com/v2/Compliance/ContinuousComplianceNotification/PublishOpenedFindings/' + notificationpolicyid
    urldata = {"notificationTargets":["IndexElasticSearch"],"specificPolicies":[compliancepolicyid]}
    headers = {'content-type': 'application/json'}
    print('Creating Continuous Compliance Policy')

    try:
        resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
        
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}') 
    else:
        print('Success!')

    if resp.status_code == 201:
        resp = json.loads(resp.content)
        print('Dome9 Send all alerts successful. workflowId: ' + resp['workflowId'])
        return resp['workflowId']
    
    elif resp.status_code == 400:
        print('Dome9 Send all alerts bad request.')
        print(resp)

    else:
        print('Error when attempting to send all alerts.')
        print(resp)
        return False

def run_assessment(d9cloudaccountid, rulesetid):
    url = "https://api.dome9.com/v2/assessment/bundleV2"
    urldata = {"Id": rulesetid, "CloudAccountId": d9cloudaccountid, "CloudAccountType": cloudid, "Region":""}
    headers = {'content-type': 'application/json'}
    print('Calling the Dome9 API to run compliance assessment.')

    resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)

    if resp.status_code == 200:
        resp = json.loads(resp.content)
        print('Compliance Assessment completed successfully. \nView report at: https://secure.dome9.com/v2/compliance-engine/result/' + str(resp['id']))
        return True
    
    else:
        print('Error when attempting to run assessment.')
        print(resp.content)
        return False
    
def remove_aws_account(accountid):
    print('test')


# Main
def main(argv=None):

    global OPTIONS, d9id, d9secret, cloudid
    account_added = ''
    notification_added = ''

    config = configparser.ConfigParser()
    config.read("./d9_account.conf")

    # set up our Dome9 API endpoint(s) and other Dome9 dependencies
    global d9id, d9secret
    d9id = config.get('dome9', 'd9id')
    d9secret = config.get('dome9','d9secret')

# handle arguments
    if argv is None:
        argv = sys.argv[2:]
#DUMP ARGV log

    parser = argparse.ArgumentParser("%prog <aws|azure|gcp> [options] ")
    parser.add_argument("--name", dest="accountname", help="Cloud account friendly name")
    parser.add_argument("--arn", dest="arn", help="AWS Role ARN for Dome9")
    parser.add_argument("--externalid", dest="externalid", help="AWS external ID used for Dome9 Role")
    parser.add_argument("--email", dest="email", help="E-mail Address")
    parser.add_argument("--sync", dest="sync", help="Time to wait after account onboarded (in minutes)")

    OPTIONS = parser.parse_args(argv)

    if len(sys.argv) == 1:
        parser.print_help()
        os._exit(1)

    mode = sys.argv[1]
    print("Mode: " + mode)

    if mode == '-h' or mode == '--help':
        parser.print_help()
        os._exit(1)

    if mode == 'aws':
        rulesetid = -16
        cloudid = 1
        arnparse = OPTIONS.arn.split(':')
        extaccountid = arnparse[4]
        print('Cloud Account ID: ' + extaccountid)
        #account_added = add_aws_account(d9id, d9secret, OPTIONS.accountname, OPTIONS.arn, OPTIONS.externalid)
        account_added = '786df20e-1bed-4615-9d19-98da3255fa0c' #testing

        if account_added:
            print('Waiting for initial account sync')
            #syncwait = OPTIONS.sync * 60
            #sleep(syncwait)
            notification_name = OPTIONS.accountname + '_' + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(5))
            notification_policy_added = add_notification_policy(notification_name, OPTIONS.email)
            cc_policy_added = add_cc_policy(account_added, extaccountid, notification_policy_added, rulesetid)
            run_assessment(account_added, rulesetid)
            sleep(5)
            send_all_alerts(notification_policy_added, cc_policy_added)

    return 0


if __name__ == "__main__":
    sys.exit(main())