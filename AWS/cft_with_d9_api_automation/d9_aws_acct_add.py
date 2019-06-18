#!/usr/bin/python3

# *******************************************************************************
# Name: d9_aws_acct_add.py
# Description: A simple Dome9 script to automate the addition of an AWS account
# to a Dome9 account - including the AWS dependencies via CloudFormation template
# Author: Patrick Pushor
# todo : lambda-ize and package this via ?, add more error handling and logging
#
# Copywrite 2019, Dome9 Security
# www.dome9.com - secure your cloud
# *******************************************************************************

import json
import time
import os
import sys
import configparser
import requests
import boto3
from botocore.exceptions import ClientError
import string
from random import *
from time import sleep
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from datetime import datetime

d9id = ''
d9secret = ''

def add_aws_account_to_d9(name, arn, extid, readonly):

    url = "https://api.dome9.com/v2/CloudAccounts"
    payload = {"name": name, "credentials": {"arn": arn, "secret": extid, "type": "RoleBased", "isReadOnly": readonly}, "fullProtection": "false"}

    print('\nAdding target AWS account to Dome9...')
    resp = http_request('post', url, payload, False)
    
    if resp.status_code == 201:
        resp = json.loads(resp.content)
        return resp['id']
    
    elif resp.status_code == 400:
        print('AWS Cloud Account already added or bad request. Please remove the account from Dome9 before using this script.')
        print(payload)
    else:
        print('Error when attempting to add AWS account.')
        print(resp)
        return False      

def get_aws_accounts_from_d9():

    url = "https://api.dome9.com/v2/CloudAccounts"
    payload = {}

    print('\nGetting list of AWS accounts already onboarded to Dome9...')
    resp = http_request('get', url, payload, False)
    
    if resp.status_code == 200:
        resp = json.loads(resp.content)
        return resp
    
    else:
        print('Error when attempting to get list of AWS accounts.')
        print(resp)
        return False

def process_organizatonal_units(aws_ou_list):

    url = "https://api.dome9.com/v2/organizationalunit"
    payload = {}
 
    resp = http_request('get', url, payload, True)

    if resp.status_code == 200:
        root = json.loads(resp.content)
    
    else:
        print('Error when attempting to get OUs from Dome9.')
        print(resp)
        return False   
    
    current_d9_parent_ou = root[0]['children']

    for depth, item in enumerate(aws_ou_list):
        missing_ou = True
        for idx, ou in enumerate(current_d9_parent_ou):
            if ou['item']['name'] == aws_ou_list[depth]:
                print(f'Found OU in Dome9: {aws_ou_list[depth]}')
                missing_ou = False
                last_ou = ou['item']['id']
                break

        if missing_ou: 
            oupath = 'ROOT/' + '/'.join(aws_ou_list)
            print(f'A Dome9 OU was not found. \nCreating all OUs within path: {oupath}')
            missing_ou_depth = depth
            while missing_ou_depth < len(aws_ou_list):
                if missing_ou_depth == 0:
                    last_ou = create_ou_in_d9(aws_ou_list[missing_ou_depth], None)
                else:
                    last_ou = create_ou_in_d9(aws_ou_list[missing_ou_depth], last_ou)
                missing_ou_depth += 1
            break
        else:            
            current_d9_parent_ou = current_d9_parent_ou[idx]['children']
    
    return last_ou

def create_ou_in_d9(name, parent_id):

    url = "https://api.dome9.com/v2/organizationalunit"
    payload = {"name":name,"parentId":parent_id}

    print(f'\nCreating OU in Dome9: {name}')
    resp = http_request('post', url, payload, False)
    
    if resp.status_code == 200:
        resp = json.loads(resp.content)
        return resp['item']['id']
    
    else:
        print('Error when attempting to create OU in Dome9.')
        print(resp)
        return False

def attach_account_to_ou_in_d9(cloud_account_id, ou_id):        

    url = "https://api.dome9.com/v2/cloudaccounts/organizationalunit/attach"
    payload = {"entries":[cloud_account_id],"organizationalUnitId":ou_id}

    print('\Attaching Cloud Account to OU...')
    resp = http_request('post', url, payload, False)
    
    if resp.status_code == 200:
        resp = json.loads(resp.content)
        return resp
    
    else:
        print('Error when attempting to attach AWS account to Dome9 OU.')
        print(resp)
        return False    
        
def get_aws_org_parent(orgclient, id):
    try: 
        parentresp = orgclient.list_parents(
            ChildId=id,
            MaxResults=10
        )['Parents'] 

        if parentresp[0]['Type'] == 'ORGANIZATIONAL_UNIT':
            ouresp = orgclient.describe_organizational_unit(
                OrganizationalUnitId=parentresp[0]['Id']
            )['OrganizationalUnit']
            return ouresp
        elif parentresp[0]['Type'] == 'ROOT':
            return False
    except ClientError as e:
        print(f'Unexpected error: {e}')
        
def get_aws_org_ou_flat_list(orgclient, aws_account):
    ou_list = []
    current_parent = get_aws_org_parent(orgclient, aws_account)
    if current_parent:
        ou_list.append(current_parent['Name'])
    else:
        return ou_list
        
    while current_parent:
        current_parent = get_aws_org_parent(orgclient, current_parent['Id'])
        if current_parent:
            ou_list.insert(0, current_parent['Name'])

    if len(ou_list) > 5:
        print(f'ERROR: OUs have exceeded the depth limit of 5: \n{ou_list}')
        os._exit(1)
    else: 
        return ou_list

def get_cft_stack(cfclient, name):
    try: 
        resp = cfclient.describe_stacks(
        StackName=name,
        )['Stacks'] 
        return resp[0]
    except ClientError as e:
        print(f'Unexpected error: {e}')
            
def check_cft_stack_exists(cfclient, name):
    try:
        stacks = cfclient.list_stacks()['StackSummaries']
        for stack in stacks:
            if stack['StackStatus'] == 'DELETE_COMPLETE':
                continue
            if name == stack['StackName']:
                return True
    except ClientError as e:
        print(f'Unexpected error: {e}')
        return False
        
def create_cft_stack(cfclient, name, cfturl, extid):
    try:
        resp = cfclient.create_stack(
            StackName=name,
            TemplateURL=cfturl,
            Parameters=[
                {
                    'ParameterKey': 'Externalid',
                    'ParameterValue': extid
                    },
            ],
            Capabilities=['CAPABILITY_IAM'],
            )
        return resp
    except ClientError as e:
        print(f'Unexpected error: {e}')
        return False

def sync_aws_org(orgclient, stsclient):
    # Get AWS accounts from Orgs and iterate through the pages to create a list
    org_accounts_raw = orgclient.list_accounts(MaxResults=20)
    org_accounts_pruned = []

    for account in org_accounts_raw['Accounts']:
        org_accounts_pruned.extend( [{'id': account['Id'], 'name': account['Name']}] )

    if 'NextToken' in org_accounts_raw:
        next_token = True
    else:
        next_token = False

    while next_token:
        print('Fetching next page of accounts...')
        org_accounts_raw = orgclient.list_accounts(NextToken=org_accounts_raw['NextToken'], MaxResults=20)
        for account in org_accounts_raw['Accounts']:
            org_accounts_pruned.extend([{'id': account['Id'], 'name': account['Name']}])        
        if 'NextToken' in org_accounts_raw:
                next_token = True
        else:
            next_token = True
            print('\nEnd of cloud acounts list.')
            break

    # Get AWS accounts from Dome9 and iterate through to create a list    
    d9_aws_accounts_raw = get_aws_accounts_from_d9()
    d9_aws_accounts_pruned = []
    for account in d9_aws_accounts_raw:
        d9_aws_accounts_pruned.extend([{'id': account['externalAccountNumber']}])      
    #print(f'AWS:\n{org_accounts_pruned}')
    #print(f'D9:\n{d9_aws_accounts_pruned}')

    temp_d9_list = {(d['id']) for d in d9_aws_accounts_pruned}
    unprotected_account_list = [d for d in org_accounts_pruned if (d['id']) not in temp_d9_list]

    if len(unprotected_account_list) == 0:
        print("No unprotected accounts found.")
        os._exit(1)
    print(f'Found the following unprotected AWS Accounts: \n{unprotected_account_list}')

    for account in unprotected_account_list:
        roleSuffix = 'MattsOrgRole' #hardcoded, needs to change
        assumeRoleArn = 'arn:aws:iam::' + account['id'] + ':role/' + roleSuffix
        print(assumeRoleArn) 
        stsresp = stsclient.assume_role(
         RoleArn=assumeRoleArn,
         RoleSessionName='DeployDome9CFTSession',
         DurationSeconds=1800
         )

        cfclient = boto3.client('cloudformation',
         aws_access_key_id=stsresp['Credentials']['AccessKeyId'],
         aws_secret_access_key=stsresp['Credentials']['SecretAccessKey'],
         aws_session_token=stsresp['Credentials']['SessionToken'],
         region_name=region_name
         )
        aws_ou_list = get_aws_org_ou_flat_list(orgclient, account['id'])
        if aws_ou_list:
            d9_ou_id = process_organizatonal_units(aws_ou_list)
            d9_cloud_account_id = process_account(cfclient, account['name'])
            attach_account_to_ou_in_d9(d9_cloud_account_id, d9_ou_id)

def process_account(cfclient, aws_account_name):
    # Check if the CFT Stack exists from a previous run
    d9stack = 'Dome9PolicyAutomated'
    if check_cft_stack_exists(cfclient, d9stack):
        print('Stack exists.  Perhaps this script has already been run?')
        os._exit(1)
    
    print('\nProvisioning the CloudFormation stack in AWS...')
    extid = ''.join(choice(string.ascii_letters + string.digits) for _ in range(24))
    stack_created = create_cft_stack(cfclient, d9stack, cfts3path, extid)

    #CHECK CFT STATUS
    t = 0
    while t < 20:
        t += 1
        stack = get_cft_stack(cfclient, d9stack)
        if stack['StackStatus'] not in ['CREATE_IN_PROGRESS','CREATE_COMPLETE']:
            print(f'Something went wrong during CFT stack deployment: {stack["StackStatus"]}')
            os._exit(1)
        elif stack['StackStatus'] == 'CREATE_COMPLETE':
            print('Success! Stack created.')
            break
        else:
            print(f'... Try {t}/20: {stack["StackStatus"]}')
            sleep(15)            
    
    # Get CFT Stack info to pull the Role ARN
    cftstack = get_cft_stack(cfclient, d9stack)
    rolearn = False
    for output in cftstack['Outputs']:
        if output['OutputKey'] == 'RoleARNID':
            rolearn=output['OutputValue']

    # Add the AWS account to Dome9
    print('\nAdding AWS account to Dome9...')
    d9_account_added = add_aws_account_to_d9(aws_account_name, rolearn, extid, d9readonly)
    print(d9_account_added)
    return d9_account_added
    
def http_request(request_type, url, payload, silent): 

    # request_type = post/delete/get
    request_type = request_type.lower()
    # silent = True/False

    headers = {'content-type': 'application/json'}
    resp = ''
    try:
        if request_type.lower() == 'post':
            resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=payload, headers=headers)
        elif request_type.lower() == 'delete':
            resp = requests.delete(url, auth=HTTPBasicAuth(d9id, d9secret), json=payload, headers=headers)
        elif request_type.lower() == 'get':
            resp = requests.get(url, auth=HTTPBasicAuth(d9id, d9secret), json=payload, headers=headers)
        else:
            print('Request type not supported.')
            return False
        
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}')  
    else:
        if not silent:
            print('Success!')
    
    return resp

def main():
    print(f'\n:: Dome9 AWS Onboarding with CFT Deployment Automation :: \nExecution time: {str(datetime.now())} \n')  # Got an error? You need Python 3.6 or later.
    global d9id, d9secret, region_name, cfts3path, d9readonly

    # handle arguments
    if len(sys.argv) > 1: 
        aws_account_name = sys.argv[1]
    else:
        print('ERROR: AWS account name parameter not set at command line.')
        os._exit(1)
        
    # load config file
    config = configparser.ConfigParser()
    config.read("./d9_aws_acct_add.conf")

    # Get Dome9 API credentials from env variables or config file
    try:
        d9id = os.environ['d9id']
        d9secret = os.environ['d9secret']
        d9mode = os.environ['d9mode']
        print('Environment variables found for Dome9 API credentials.')
    except KeyError: 
        print('Reading config file for Dome9 API credentials...')
        d9id = config.get('dome9', 'd9id')
        d9secret = config.get('dome9','d9secret')
        if d9id and d9secret:
             print('Success!')
        else:
            print('Dome9 API credentials not found in environment variables or configuration file.')
            os._exit(1)

    if not d9id or not d9secret or not d9mode:
        print ('Please ensure that all config settings in d9_aws_acct_add.conf are set.')
        os._exit(1)
        
    # set up our AWS creds for the client. Region is required but not used.
    try:
        awsaccesskey = config.get('aws', 'awsaccesskey')
        awssecret = config.get('aws', 'awssecret')
        region_name = config.get('aws', 'region_name')
        cfclient = boto3.client('cloudformation',
         aws_access_key_id=awsaccesskey,
         aws_secret_access_key=awssecret,
         region_name=region_name
         )
        orgclient = boto3.client('organizations',
         aws_access_key_id=awsaccesskey,
         aws_secret_access_key=awssecret,
         region_name=region_name
         )
        stsclient = boto3.client('sts',
         aws_access_key_id=awsaccesskey,
         aws_secret_access_key=awssecret,
         region_name=region_name
         )
    except KeyError:
        print('\nAWS credentials not found in config file. Using AWS credentials from IAM Role...')
        cfclient = boto3.client('cloudformation', region_name=region_name)       
        orgclient = boto3.client('organizations', region_name=region_name)   
        stsclient = boto3.client('sts', region_name=region_name)

    # Deploy the respective CFT for the mode
    if d9mode == ('readonly'):
        cfts3path = config.get('aws', 'cfts3pathro')
        d9readonly = True
    elif d9mode == ('readwrite'):
        cfts3path = config.get('aws', 'cfts3pathrw')
        d9readonly = False
    else:
        print ('Set the Dome9 account mode (readonly/readwrite) in the config file...')
        os._exit(1)

    sync_aws_org(orgclient, stsclient)
    
    return 0

if __name__ == '__main__': main()
