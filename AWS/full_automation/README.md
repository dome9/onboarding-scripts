# Dome9 Full Automation of AWS Account Onboarding

This is a fully automated solution to onboard accounts into Dome9 using three options:
* Simple onboarding of the AWS account that is running the script
* Cross-account onboarding of child accounts from a parent AWS account
* AWS Organizations synchronization of accounts and organizational units (OUs) for onboarding

#### How it works
There are CloudFormation templates (CFTs) staged in S3 which are used to create an IAM policy and cross-account access role in each target AWS account to be onboarded in Dome9. There are two CFTs to choose from, depending on the desired Dome9 mode: read-only or read-write. Once the CloudFormation stack is successfully deployed, the script will then add the target account into Dome9. If you are using AWS Organizations, the target account will discovered automatically and onboarded in Dome9.

## **Process Summary** 
The following explains what this tool does in sequence at a high level:
1. [Organizations Mode] Discover AWS child accounts and their respective OUs from AWS Organziations and compare them against Dome9.
2. [Organizations/Cross-account Mode] Assume-role into AWS child accounts to create a CloudFormation stack.
3. Check if a CloudFormation stack for Dome9 already exists in the region.
4. Randomly generate an external ID for a cross-account access role.
5. Deploy the respective CFT for the Dome9 selected mode (read-only/read-write), creating a new cross-account access role.
6. Wait until the CFT deployment is completed.
7. Pull outputs from CloudFormation stack.
8. Add AWS Account to Dome9.
9. [Organizations Mode] Place the target AWS Account into a Dome9 OU which mirrors the AWS Organizations OU.

## Requirements
* IAM permissions to create CloudFormation Stacks, IAM Policies, and IAM Roles in target AWS accounts.
* Python v3.6 or later. 
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
	Verify: `python3 --version`
* Git Command Line Tools
	```bash
	# Intall Git on RHEL
	sudo yum install git -y
	```
	```bash
	# Install Git on Ubuntu
	sudo apt-get install git -y
	```
	Verify: `git --version`

## Assumptions
The following assumptions are made about the environment to be successful running the script.
* AWS Organizations Onboarding
  * Any account in AWS Organizations has a cross-account access role in the child account with a consistent name (e.g. MyOrgsAdminRole) and with minimal IAM permissions. The parent account will assume the role in the child account. Not having a consistent role name will require running the script multiple times. Below is an example of the IAM policy required to be attached to the role in order to onboard the child account into Dome9 using this script:	
	```json
	{
	    "Version": "2012-10-17",
	    "Statement": [
	        {
	            "Sid": "D9FULLAUTOMATIONCHILDACCOUNT",
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

### Step 1: Clone the repo and Install Dependencies
1. Clone this repo into your local environment
	`git clone https://github.com/Dome9/onboarding-scripts.git`

2. Navigate to the script subdirectory:
	`cd onboarding-scripts/AWS/full_automation`

3. Using PIP, install the following python dependencies:
   * boto3
   * requests
	```bash
	# Install python dependencies
	pip3 install boto3 requests
	```

### Step 2:  Upload Dome9 Platform CFTs to an S3 bucket
1. Upload CloudFormation templates to an accessible S3 bucket. They can be found [here](https://github.com/Dome9/onboarding-scripts/tree/master/AWS/cloudformation).
   **Optional**: Use the public CFT URLs predefined in the `d9_onboard_aws.conf` file and skip the rest of this section.
2. Edit  `d9_onboard_aws.conf`.
3. Set the S3 URLs for `cft_s3_url_readonly` and `cft_s3_url_readwrite`
4. Save the file.

### Step 3: Setup Dome9 Environment Variables

1. Create your Dome9 V2 API Credentials [here](https://secure.dome9.com/v2/settings/credentials).
2. Set the environment variables.
	```bash
	# Dome9 V2 API Credentials Example
	export d9id=12345678-1234-1234-1234-123456789012
	export d9secret=abcdefghijklmnopqrstuvwx
	```
### Step 4: Setup AWS Credentials for Parent AWS Account

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

## Operation
To run the script, review the run modes of the script and the arguments for each mode.

### Run Modes
The first argument in the command string determines the run mode of the script. Below is a list of the available run modes.
Syntax: `python d9_onboard_aws.py <mode> [options]`

| Run Mode         | Description                        
|------------------|---------------------------------------------------------------|
| `local`          | Onboard the AWS account running the script only  |
| `crossaccount`   | Onboard an AWS account using Assume-Role |
| `organizations`  | Onboard parent and child accounts and attach them to Dome9 organizational units mapped from AWS Organizations metadata |

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