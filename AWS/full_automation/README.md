


# Dome9 Full Automation of AWS Account Onboarding

This is a fully automated solution to onboard accounts into Dome9 using three options:
* Simple onboarding of an AWS account using local IAM users or roles 
* Cross-account onboarding of child accounts from a parent AWS account
* AWS Organizations synchronization of accounts and organizational units (OUs) for onboarding

#### How it works
There are CloudFormation templates (CFTs) staged in S3 which are used to create an IAM policy and cross-account access role in each target AWS account to be onboarded to Dome9. There are two CFTs to choose from, depending on the desired Dome9 mode: read-only or read-write. Once the CloudFormation stack is successfully deployed, the script will then add the target account into Dome9. If you are using AWS Organizations, the target account will be placed in the appropriate Dome9 OU.

## **Process Summary** 
The following explains what this tool does in sequence at a high level:
1. [Organizations Mode] Discover AWS subaccounts and their respective OUs from AWS Organziations.
2. [Organizations Mode] Compare it to the accounts already onboarded to Dome9 and generate a list of accounts to onboard.
3. [Organizations/Cross-account Mode] Assume-role into those accounts using an cross-account access role.
4. Check if a CloudFormation stack for Dome9 already exists in the region.
5. Randomly generate an external ID for a cross-account access role.
6. Deploy the respective CFT for the Dome9 mode selected (read-only/read-write), creating a cross-account access role.
7. Wait until the CFT deployment is completed.
8. Pull outputs from CFT stack.
9. Add AWS Account to Dome9.
10. [Organizations Mode] Place the target AWS Account into a Dome9 OU which mirrors the AWS Organizations OU.

## Requirements
* IAM permissions to create CloudFormation Stacks, IAM Policies, and IAM Roles in target AWS accounts.
* Python v3.6 or later. Verify: `python3 --version`
	```bash
	# Install Python v3.6 and PIP on RHEL 8 
	sudo yum update
	sudo yum install python36 python3-pip -y
	```
	```bash
	# Install Python v3.6 and PIP on Ubuntu 18.04
	sudo apt-get update
	sudo apt-get install python3 python3-pip -y
	```
* Install Git. Verify: `git --version`
	```bash
	# Intall Git on RHEL
	sudo yum install git -y
	```
	```bash
	# Install Git on Ubuntu
	sudo apt-get install git -y
	```

## Assumptions
The following assumptions are made about the environment to be successful running the script.
* AWS Organizations Onboarding
  * Any account created in AWS Organizations has a cross-account access role with a consistent name (e.g. MyOrgsAdminRole) and with the minimal IAM permissions. The parent account will assume-role of the child account with this role. Not having a consistent role name will require running the script multiple times. Below is an example of the IAM policy required to be attached to the role in order to onboard the account into Dome9 using this script:	
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
* Cross-account Onboarding
  * The `crossaccount` mode requires the same IAM permissions in the target accounts as above. 

## Setup

### Step 1:  Upload Dome9 Platform CFTs to an S3 bucket
1. Upload CloudFormation templates to an accessible S3 bucket. They can be found [here](https://github.com/Dome9/onboarding-scripts/tree/master/AWS/cloudformation).
   **Optional**: Use the public CFT URLs predefined in the `d9_onboard_aws.conf` file and skip the rest of this section.
2. Edit  `d9_onboard_aws.conf`.
3. Set the S3 URLs for `cft_s3_url_readonly` and `cft_s3_url_readwrite`
4. Save the file.

### Step 2: Setup Dome9 Environment Variables

1. Create your Dome9 V2 API Credentials [here](https://secure.dome9.com/v2/settings/credentials).
2. Set the environment variables.
	```bash
	# Dome9 V2 API Credentials Example
	export d9id=12345678-1234-1234-1234-123456789012
	export d9secret=abcdefghijklmnopqrstuvwx
	```
### Step 3: Setup AWS Credentials for Parent AWS Account

1. Get IAM Credentials
   - Option 1: Run the script on an AWS resource which uses a service-linked role. The script will dynamically find the credentials without the need to specify environment variables.
   - Option 2: Create IAM User access keys and set the environment variables. 
		```bash
		# AWS Credentials Example
		export AWS_ACCESS_KEY_ID=AK00012300012300TEST
		export AWS_SECRET_ACCESS_KEY=Nnnnn12345nnNnn67890nnNnn12345nnNnn67890
		```
2. Attach the following IAM Policy to the service-linked role or IAM user that you created.
	```json
	{
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
### Step 4 : Install Python Dependencies
Using PIP, install the following python dependencies:
* boto3
* requests
  ```bash
  # Install python dependencies
  pip3 install boto3 requests
  ```


## Operation
To run the script, review the run modes of the script and the arguments for each mode.

### Run Modes
The first argument in the command string determines the run mode of the script. Below is a list of the available run modes.
Syntax: `python d9_onboard_aws.py <mode> [options]`

| Run Mode         | Description                        
|------------------|---------------------------------------------------------------|
| `local`          | Onboard the AWS account running the script only  |
| `crossaccount`   | Onboard an AWS account using Assume-Role |
| `organizations`  | Onboard parent and subaccounts and attach them to Dome9 organizational units mapped from AWS Organizations metadata |

### Global and Mode-specific Arguments 
Below are the global and mode-specific arguments.

* **Global**
  Global arguments are required for all run modes. 

  * | Argument         | Description                                               | Default value |
    |------------------|-----------------------------------------------------------|---------------|
    | `--region`       | AWS Region Name for Dome9 CFT deployment.                 | `us-east-1` |
    | `--d9mode`       | readonly/readwrite: Dome9 mode to onboard AWS account as. | `readonly`  |
    > Note: If global arguments are missing, the script will assume default values.

* **Local Mode**
   * | Argument | Description                                           | Example value |
     |----------|-------------------------------------------------------|---------------|
     | `--name` | Cloud account friendly name in quotes  (**required**) | `"AWS PROD"`  |

* **Crossaccount Mode**
   * | Argument    | Description                                                  | Example value |
     |-------------|--------------------------------------------------------------|---------------|
     | `--account` | Cloud account number (**required**)                          | `987654321012` |
     | `--name`    | Cloud account friendly name in quotes (**required**)         | `"AWS PROD"` |
     | `--role`    | AWS cross-account access role for Assume-Role (**required**) | `MyRoleName` |

* **Organizations Mode**
   * | Argument            | Description                                                  | Example value |
     |---------------------|--------------------------------------------------------------|--------------|
     | `--role`            | AWS cross-account access role for Assume-Role (**required**) | `MyRoleName` |
     | `--ignore-ou`       | Ignore AWS Organizations OUs and place accounts in root.     | |
     | `--ignore-failures` | Ignore onboarding failures and continue.                     |

### How to run:
```bash
# Syntax
python d9_onboard_aws.py <local|crossaccount|organizations> [options]
# Help with run modes
python d9_onboard_aws.py local --help
python d9_onboard_aws.py crossaccount --help
python d9_onboard_aws.py organizations --help
# Example of each mode
python d9_onboard_aws.py local --name "AWS DEV" --d9mode readonly --region us-east-1
python d9_onboard_aws.py crossaccount --account 987654321012 --name "AWS DEV" --role MyRoleName --d9mode readonly --region us-east-1
python d9_onboard_aws.py organizations --role MyRoleName --d9mode readonly --region us-east-1 --ignore-failures
```