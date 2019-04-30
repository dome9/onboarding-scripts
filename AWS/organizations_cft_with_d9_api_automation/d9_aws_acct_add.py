#!/usr/bin/python

# *******************************************************************************
# Name: d9_aws_acct_add.py
# Description: A simple Dome9 script to automate the addition of an AWS account
# to a Dome9 account - including the AWS dependencies via CloudFormation template
#
# Copywrite 2019, Check Point Software
# *******************************************************************************

import json
import time
import sys
import configparser
import requests
import boto3
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
    url = "https://api.dome9.com/v2/CloudAccounts"

    # set up our AWS creds and other AWS dependencies
    awskey = config.get('aws', 'awskey')
    awssecret = config.get('aws', 'awssecret')
    region_name = config.get('aws', 'region_name')

    #if d9id or d9secret or d9mode or awskey or awssecret == "":
    #    print ('Please ensure that all config settings in d9_aws_acct_add.conf are set.')
    #    sys.exit()

    if d9mode == ('readonly'):
        cfts3path = config.get('aws', 'cfts3pathro')
        d9readonly = ('true')
    elif d9mode == ('readwrite'):
        cfts3path = config.get('aws', 'cfts3pathrw')
        d9readonly = ('false')
    else:
        print ('Set the Dome9 account mode (readonly vs readwrite) in the config file...')
        sys.exit()

    # Connect to AWS - region doesn't have meaning here since we are calling global services, but is required.

    orgclient = boto3.client('organizations',
    aws_access_key_id=awskey,
    aws_secret_access_key=awssecret,
    region_name=region_name
    )

    resp = orgclient.list_accounts(
    #NextToken='str',
    MaxResults=20
    )
    
    orgResp = resp['Accounts']

    orgAccount = []
    for i in range(len(orgResp)):
        orgAccount.extend( [{'id': orgResp[i]['Id'], 'name': orgResp[i]['Name']}] )
    print(orgAccount)
  
    stsclient = boto3.client('sts',
    aws_access_key_id=awskey,
    aws_secret_access_key=awssecret,
    region_name=region_name
    )

    # Make the API call to Dome9 to get list of AWS accounts already onboarded

    headers = {'content-type': 'application/json'}

    resp = requests.get(url, auth=HTTPBasicAuth(d9id, d9secret), headers=headers)
    
    resp = json.loads(resp.content)

    d9onboardedAwsAccount = []
    for i in range(len(resp)):
        d9onboardedAwsAccount.extend([{'id': resp[i]['externalAccountNumber']}])
    print(d9onboardedAwsAccount)

    processAccount = orgAccount
    for i in range(0,len(processAccount)):
        for j in range(0, len(d9onboardedAwsAccount)):
            if (processAccount[i]['id']) == (d9onboardedAwsAccount[j]['id']):
                print('found match')
                del orgAccount[i]
                break
   
    print(orgAccount)
    
    sys.exit()
    
    unprotectedAccount = set(orgAccount) - set(d9onboardedAwsAccount)

    if len(unprotectedAccount) == 0:
        print("No unprotected accounts found.")
        sys.exit()
    else:
        print('Found the following unprotected AWS Accounts:')
        print(unprotectedAccount)

    #for i in range(len(orgResp)):
       

    
    # Create CF Stack and add account to Dome9
    assumeRoleArn='arn:aws:iam::789630564330:role/MattsOrgRole'
    
    stsResponse = stsclient.assume_role(
    RoleArn=assumeRoleArn,
    RoleSessionName='DeployDome9CFTSession',
    DurationSeconds=1800
    )

    cfclient = boto3.client('cloudformation',
    aws_access_key_id=stsResponse['Credentials']['AccessKeyId'],
    aws_secret_access_key=stsResponse['Credentials']['SecretAccessKey'],
    aws_session_token=stsResponse['Credentials']['SessionToken'],
    region_name=region_name
    )
    
    cfclient.describe_stacks()
    d9stack=('Dome9PolicyAutomated')

    def _stack_exists(stack_name):
        stacks = cfclient.list_stacks()['StackSummaries']
        for stack in stacks:
            if stack['StackStatus'] == 'DELETE_COMPLETE':
                continue
            if stack_name == stack['StackName']:
                return True
        return False

    if _stack_exists(d9stack):
            print('Stack exists.  Perhaps this script has already been run?')
            sys.exit()

    # submit the appropriate CFT

    allchar = string.ascii_letters + string.digits
    extid = "".join(choice(allchar) for x in range(randint(12, 18)))

    print('Provisioning the CloudFormation stack @ AWS.')

    response = cfclient.create_stack(
        StackName=d9stack,
        TemplateURL=cfts3path,
        Parameters=[
            {
                'ParameterKey': 'Externalid',
                'ParameterValue': extid
                },
        ],
        Capabilities=['CAPABILITY_IAM'],
        )

    # This should be a loop iterating through the status of the CF stack
    # provisioning until it's finished

    print('Providing time for the CF stack to finish provisioning... (about two minutes).')
    time.sleep(120)

    # measure the ARN of the role in the stack we created and store it

    cftoutput = cfclient.describe_stacks(
    StackName=d9stack,
    )

    RoleARNID=False

    for output in cftoutput[u'Stacks'][0][u'Outputs']:
        if output[u'OutputKey']=='RoleARNID':
            RoleARNID=output[u'OutputValue']

    # Make the API call to Dome9 to add Cloud Account

    urldata = {"name": accountsList[x]['Name'], "credentials": {"arn": RoleARNID, "secret": extid, "type": "RoleBased", "isReadOnly": d9readonly}, "fullProtection": "false"}
    headers = {'content-type': 'application/json'}

    print('Calling the Dome9 API with all required info to add your AWS account.')

    resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
    print (resp.content)

if __name__ == '__main__': run()
