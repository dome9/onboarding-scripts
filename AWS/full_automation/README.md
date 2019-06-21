# **Dome9 Full Automation of AWS Account Onboarding** #

This is the fully automated option that will create the cross-account role on the target account, and then link the account to Dome9 via API. 

This is a simple example script to understand how to leverage automation,
including both AWS CloudFormation templates and this script, to add an AWS
account to a Dome9 account.

## **Process Summary** ##
The following explains what this tool does in sequence:
1. Check if a AWS CFT stack conflict exists.
2. Randomly generate an external ID for the IAM cross-account access role.
3. Deploy the respective CFT for the Dome9 mode selected.
4. Wait until the CFT deployment is completed
5. Pull outputs from CFT stack
6. Add AWS Account to Dome9

## Requirements ##
* Python 3.6 or later. Verify: ```python3 --version```
* Permissions to create IAM policies in targets AWS accounts.

###IAM Policy for Parent###
This IAM policy is attached to a IAM user or role in the parent AWS account.
```json
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "D9FULLAUTOMATIONPARENT",
            "Effect": "Allow",
            "Action": [
                "iam:ListPolicies",
                "iam:GetRole*",
                "iam:ListRole*",
                "iam:PutRolePolicy",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:CreatePolicy",
                "cloudformation:List*",
                "cloudformation:Create*",
                "cloudformation:Describe*",
                "sts:*",
                "organizations:Describe*",
                "organizations:List*"
            ],
            "Resource": "*"
        }
    ]
}
```

### IAM Policy for Subaccounts ###
This IAM policy is attached to a cross-account access role in AWS subaccounts.
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "D9FULLAUTOMATIONSUBACCOUNT",
            "Effect": "Allow",
            "Action": [
                "iam:ListPolicies",
                "iam:GetRole*",
                "iam:ListRole*",
                "iam:PutRolePolicy",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:CreatePolicy",
                "cloudformation:List*",
                "cloudformation:Create*",
                "cloudformation:Describe*"
            ],
            "Resource": "*"
        }
    ]
}
```
## Setup

- Upload CloudFormation templates to an S3 bucket. They can be found at: https://github.com/Dome9/onboarding-scripts/tree/master/AWS/cloudformation
Optional: Use the hosted CFTs in the config file. 

- Set Dome9 environment variables
```bash
# Environment Variable Examples
# Dome9 V2 API Credentials
export d9id=12345678-1234-1234-1234-123456789012
export d9secret=abcdefghijklmnopqrstuvwx
```
- Set AWS environment variables for IAM User ()
```bash
# AWS Credentials
export AWS_ACCESS_KEY_ID=AK00012300012300TEST
export AWS_SECRET_ACCESS_KEY=Nnnnn12345nnNnn67890nnNnn12345nnNnn67890
```

- Create IAM user access keys or use a IAM role for your server.
API.  These credentials must have rights to create IAM roles and policies, as
well for the CloudFormation provisioning process to work.

- Note the https based path and filename of each of these CFTs and record them in
the d9_aws_acct_add.conf file.

- Ensure that both your Dome9 API keys and AWS API keys exist in this file as
well.

- Set region_name to the region you would like this CloudFormation template to be deployed to

- The last element of configuration in the .conf file is d9mode.  This can be one
of readwrite or readonly.  Case matters.

- Install dependencies
```bash
pip3 install boto3 requests
```


## Operation

### How to run:
```bash
# Syntax
python3 d9_onboard_aws.py <local|crossaccount|organizations> [options]
#Help with modes
d9_onboard_aws.py local --help
d9_onboard_aws.py crossaccount --help
d9_onboard_aws.py organizations --help
#Examples
d9_onboard_aws.py local --name "AWS DEV" --d9mode readonly --region us-east-1
d9_onboard_aws.py crossaccount --account 987654321012 --name "AWS DEV" --role MyRoleName --d9mode readonly --region us-east-1
d9_onboard_aws.py organizations --role MyRoleName --d9mode readonly --region us-east-1 --ignore-failures
```

### Command Line Modes ###
The mode indicates the method to onboard AWS accounts:
* ```local``` : Onboard local account running the script only
* ```crossaccount``` : Onboard subaccounts from a parent account using Assume-Role
* ```organizations``` : Onboard parent and subaccounts into Dome9 organizational units which are discovered and mapped from AWS Organizations metadata

### Command Line Arguments ###
Common Arguments
* ```--region``` : AWS Region Name for Dome9 CFT deployment. Default: us-east-1 
* ```--d9mode``` : readonly/readwrite: Dome9 mode to onboard AWS account as. Default: readonly

"local" Mode Arguments
* ```--name``` : TCloud account friendly name in quotes, e.g. "AWS PROD" (**required**)

"crossaccount" Mode Arguments
* ```--account``` : Cloud account number, e.g. 987654321012 (**required**)
* ```--name``` : Cloud account friendly name in quotes, e.g. "AWS PROD"(**required**)
* ```--role``` : AWS cross-account access role for Assume-Role, e.g. MyRoleName (**required**)

"organizations" Mode Arguments
* ```--role``` : AWS cross-account access role for Assume-Role, e.g. MyRoleName (**required**)
* ```--ignore-ou``` : GCP-specific Dome9 Compliance Ruleset ID. Default: 
* ```--ignore-failures``` : Ignore onboarding failures and continue. Default: False