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
* IAM User or cross-account access role or with administrative the following minimum permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "D9FULLAUTOMATION",
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
                "organizations:Describe*",
                "organizations:List*"
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
export d9id=dta1234d-45db-4b0f-a323-e1234e89te5t
export d9secret=tfd3gt5ghq54a754szaqgnsx
```
- Set AWS environment variables for IAM User ()
```bash
# AWS Credentials
export AWS_ACCESS_KEY_ID=AKIAX775UPGPTJTQTEST
export AWS_SECRET_ACCESS_KEY=B1s03HTxIbDciw7EvzZg55hKG1d0kOjZY09xtesT
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
python3 d9_aws_acct_add.py <mode> [aws_account_name]
#Help with modes
d9_onboard_aws.py local --help
d9_onboard_aws.py crossaccount --help
d9_onboard_aws.py organizations --help
#Examples
d9_onboard_aws.py local --name "AWS DEV" --d9mode readonly --region us-east-1
d9_onboard_aws.py crossaccount --account 987654321012 --name "AWS DEV" --role MyRoleName --d9mode readonly --region us-east-1
d9_onboard_aws.py organizations --role MyRoleName --d9mode readonly --region us-east-1 --ignore-failures True
```

You will notice that we supplied a single command line argument to the script.
This argument is what the AWS account to be added will be called in Dome9.  You
can rename an account after the fact if you desire.

If successful, the script will output the result of the API call to Dome9 to
add the account.  This is generally a fair bit of output.  This is good.  Any
errors in the process will be displayed instead of this payload of information -
if this AWS account in question is already known to Dome9, for example.

This script is very basic and could benefit from logging and error handling,
but works well and should serve to get you familiar with how this can be
accomplished.