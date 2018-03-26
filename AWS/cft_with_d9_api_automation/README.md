# Dome9 Onboarding

This is the fully automated option that will create the cross-account role on the target account, and then link the account to Dome9 via API. 


This is a simple example script to understand how to leverage automation,
including both AWS CloudFormation templates and this script, to add an AWS
account to a Dome9 account.

## Setup

- First, create or locate an S3 bucket to store the CloudFormation templates in.
They can be found at: https://github.com/Dome9/onboarding-scripts/tree/master/AWS/cloudformation

- While these templates have no sensitive information in them, choose the correct
security of this S3 bucket in accordance to what you do or plan to store within
it.  Later in the process we are going to use AWS credentials to call an AWS
API.  These credentials must have rights to create IAM roles and policies, as
well for the CloudFormation provisioning process to work.

- Note the https based path and filename of each of these CFTs and record them in
the d9_aws_acct_add.conf file.

- Ensure that both your Dome9 API keys and AWS API keys exist in this file as
well.

- The last element of configuration in the .conf file is d9mode.  This can be one
of readwrite or readonly.  Case matters.

- With all configuration file elements configured, the next piece of setup is to
install the dependencies (boto3 AWS library https://boto3.readthedocs.io/en/latest/ and requests)
```bash
pip install boto3 requests
```

- This concludes the dependencies required.

## Operation

### Call the script like this:
```bash
python d9_aws_acct_add.py "AWS Account"
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

Patrick Pushor
patrick@dome9.com
