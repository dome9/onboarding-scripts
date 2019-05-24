# **Snapshot Compliance Assessments** #
A command line tool to run a one-time snapshot compliance assessment of a cloud account.<br/>
AWS is only supported in this beta and defaults to the NIST 800-53 ruleset.

## Requirements ##
* Python 3.6 or later
* AWS account with Dome9-Connect role already deployed. You will need:
** -The Dome9 Role ARN (e.g. arn:aws:iam::012345678912:role/Dome9-Connect)
** -The External ID used for the role. (e.g. bkbj00xuTAM102IceF0s8bX6)


## Installation ##
1. Clone this repo into your local machine

```git clone https://github.com/Dome9/onboarding-scripts.git```

2. Navigate to this tool folder:

```cd onboarding-scripts/snapshot_assessment```

3. Edit d9_account.conf file with a Dome9 V2 API id and secret key.


## How to run ##
1. Using console, navigate to this tools directory (`onboarding-scripts/snapshot_assessment`)
2. Run the command 
```
Syntax: python snapshot_assessment.py <aws|azure|gcp> [options] 
python snapshot_assessment.py aws --name testaccount --arn arn:aws:iam::012345678912:role/Dome9-Connect --externalid bkbj00xuTAM102IceF0s8bX6 --email user@domain.com --delay 30
```

### Command Line arguments ###
* --name : Friendly name of the account you are onboarding (No spaces) (**required**).
* --arn : The role ARN of the AWS Dome9-Connect role (**required**). 
* --externalid : The external ID used when created the AWS Dome9-Connect role (**required**).
* --email : E-mail address to send compliance report (**required**).
* --delay : Delay (in minutes) to wait for initial cloud account sync to complete. Default is 30.
