

# Dome9 Full Automation of AWS Account Onboarding

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
* Python 3.6 or later. Verify: `python3 --version`
* Permissions to create IAM policies in targets AWS accounts.



## Setup

### Step 1:  Upload Dome9 Platform CFTs to an S3 bucket
1. Upload CloudFormation templates to an accessible S3 bucket. They can be found [here](https://github.com/Dome9/onboarding-scripts/tree/master/AWS/cloudformation).
  **Optional**: Use the public CFT URLs predefined in the `d9_onboard_aws.conf` config file. 
2. Edit  `d9_onboard_aws.conf`.
3. Set the S3 URLs for `cft_s3_url_readonly` and `cft_s3_url_readwrite`
4. Save the file.

### Step 2: Setup Dome9 Environment Variables

1. Create your Dome9 V2 API Credentials [here](https://secure.dome9.com/v2/settings/credentials).
2. Set the environment variables.
	```bash
	# Dome9 V2 API Credentials
	export d9id=12345678-1234-1234-1234-123456789012
	export d9secret=abcdefghijklmnopqrstuvwx
	```
### Step 3: Setup AWS Credentials for Parent AWS Account

1. Get IAM Credentials
   - Option 1: Run the script on an AWS resource which uses a service-linked role. The script will dynamically find the credentials without the need to specify environment variables.
   - Option 2: Create an IAM User access keys and set the environment variables. 
		```bash
		# AWS Credentials 
		export AWS_ACCESS_KEY_ID=AK00012300012300TEST
		export AWS_SECRET_ACCESS_KEY=Nnnnn12345nnNnn67890nnNnn12345nnNnn67890
		```
2. Attach the following IAM Policy to the service-linked role or IAM user that you created.
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


### Step 4 : Setup IAM resources for Parent and Cross-Accounts


#### _IAM Policy for Subaccounts_
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

#### Run Modes
The first argument in the command string determines the run mode of the script. Below is a list of the available run modes.
Syntax: `python d9_onboard_aws.py <mode> [options]`

| Run Mode         | Description                        
|------------------|---------------------------------------------------------------|
| `local`          | Onboard local account running the script only  |
| `crossaccount`   | Onboard subaccounts from a parent account using Assume-Role |
| `organizations`  | Onboard parent and subaccounts into Dome9 organizational units mapped from AWS Organizations metadata |

### Command Line Arguments ###
Below are the global and mode-specific arguments.

####  
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
