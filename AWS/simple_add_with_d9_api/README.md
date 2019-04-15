# Dome9 Onboarding

This is a simple example script to understand how to automate the processs of onboarding a cloud account via the Dome9 API. 

## Assumptions
* The AWS IAM policies and cross-account access role have already been created for Dome9. [Onboarding an AWS Account](https://helpcenter.dome9.com/hc/en-us/articles/360003994613-Onboard-an-AWS-Account)

## Setup

- Ensure that your Dome9 API ID, Dome9 API secret key, and AWS external ID exist in the config file. Typically the external ID from the Dome9 "Add AWS Cloud Account" wizard is used.

- The last element of configuration in the config file is d9mode.  This can be one
of readwrite or readonly (case sensative).

- With all configuration file elements configured, the next piece of setup is to
install the dependencies (configparser and requests)
```bash
pip install requests configparser
```

- This needs to run with Python 3+

## Operation

### Executing the script (example):
```bash
python d9_aws_acct_add.py "AWS Account Name" arn:aws:iam::123456789012:role/Dome9-Connect
```

You will notice that we supplied two command line arguments to the script.
The first argument is the friendly name of the AWS account to be added. This must be encased in quotes. You
can rename an account after the fact. The second is the AWS role ARN from the cross-account access role created for Dome9.

If successful, the script will output the result of the API call to Dome9 to
add the account.  This is generally a fair bit of output.  Any
errors in the process will be displayed instead of this payload of information -
if this AWS account in question is already known to Dome9, for example.

This script is very basic and could benefit from logging and error handling,
but works well and should serve to get you familiar with how this can be
accomplished.

## Sample output
```bash
[simple_add_with_d9_api]$ python d9_aws_acct_add.py "Alex - Sandbox" arn:aws:iam::123456789012:role/Dome9-Connect
Starting Dome9 AWS Account Add Script...
Provisioning the CloudFormation stack @ AWS.
Providing time for the CF stack to finish provisioning... (about two minutes).
Calling the Dome9 API with all required info to add your AWS account.
b'{"id":"4abce12b-cdbe-a64a-c240e5a38f06","vendor":"aws","name":"Alex - Sandbox",
"externalAccountNumber":"1234567890","error":null,"creationDate":"2018-03-26T20:08:03.6433354Z","credentials":{"apikey":null,"arn":"arn:aws:iam::123456789012:role/Dome9-Connect",
"secret":null,"iamUser":null,"type":"RoleBased","isReadOnly":true},
"iamSafe":null,"netSec":{"regions":[{"region":"us_east_1","name":"N. Virginia","hidden":true,"newGroupBehavior":"ReadOnly"},{"region":"us_west_1",
"name":"N. California","hidden":false,"newGroupBehavior":"ReadOnly"},{"region":"eu_west_1","name":"Ireland","hidden":true,"newGroupBehavior":"ReadOnly"},
{"region":"ap_southeast_1","name":"Singapore","hidden":true,
"newGroupBehavior":"ReadOnly"},{"region":"ap_northeast_1","name":"Tokyo","hidden":true,"newGroupBehavior":"ReadOnly"},{"region":"us_west_2",
"name":"Oregon","hidden":false,"newGroupBehavior":"ReadOnly"},{"region":"sa_east_1","name":"S\xc3\xa3o Paulo","hidden":true,"newGroupBehavior":"ReadOnly"},
{"region":"ap_southeast_2","name":"Sydney","hidden":true,"newGroupBehavior":"ReadOnly"},{"region":"eu_central_1","name":"Frankfurt","hidden":true,
"newGroupBehavior":"ReadOnly"},{"region":"ap_northeast_2","name":"Seoul","hidden":true,"newGroupBehavior":"ReadOnly"},{"region":"ap_south_1",
"name":"Mumbai","hidden":true,"newGroupBehavior":"ReadOnly"},{"region":"us_east_2","name":"Ohio","hidden":true,"newGroupBehavior":"ReadOnly"},
{"region":"ca_central_1","name":"Central","hidden":true,"newGroupBehavior":"ReadOnly"},{"region":"eu_west_2","name":"London","hidden":true,
"newGroupBehavior":"ReadOnly"},{"region":"eu_west_3","name":"Paris","hidden":true,"newGroupBehavior":"ReadOnly"}]},"fullProtection":false,
"allowReadOnly":false}'
```
