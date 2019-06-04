# **Dome9 Snapshot Compliance Assessment Tool** #
A command line tool to run a Dome9, one-time, snapshot compliance assessment of a cloud account.<br/>
AWS, Microsoft Azure, and Google Cloud Platform (GCP) are supported. The average runtime is about 15 minutes and will auto-cleanup upon completion.

## Process Summary ##
The following explains what this tool does in sequence:
1. Onboards target account into Dome9 using the API
2. Waits 10 minutes for initial account sync to complete 
3. Schedules a compliance assessment report to be emailed
4. Compliance assessment is triggered
5. Waits for confirmation that the compliance assessment email was sent (~7 minutes)
6. Cleanup 
   * Note: Cloud accounts are global in Dome9. If an account is not removed it will not be available for onboarding in any other Dome9 account.

## Requirements ##
* Python 3.6 or later. Verify: ```python3 --version```
* Access to IAM for a AWS, Azure, or GCP (or know who does) to create Dome9 read permissions.
* AWS account with Dome9-Connect cross-account access role deployed.
   * [ ] Create permissions for Dome9. [Manual](https://helpcenter.dome9.com/hc/en-us/articles/360003994613-Onboard-an-AWS-Account) | [CFT](https://github.com/Dome9/onboarding-scripts/tree/master/AWS/cloudformation) | [Script](https://github.com/Dome9/onboarding-scripts/tree/master/AWS/cft_with_d9_api_automation)
   * [ ] Role ARN. Account ID is derived from this. e.g. ```arn:aws:iam::012345678912:role/Dome9-Connect```
   * [ ] External ID used when creating the role. **THIS MUST MATCH**. e.g. ```bkbj00xuTAM102IceF054321```
* Azure subscription with Dome9-Connect App Registration. 
   * [ ] Create permissions for Dome9. [Manual](https://helpcenter.dome9.com/hc/en-us/articles/360003994693-Onboard-an-Azure-Subscription-to-Dome9) | [Script](https://github.com/Dome9/onboarding-scripts/tree/master/Azure) 
   * [ ] Subscription ID. e.g. ```7b7d6c48-c533-4a22-a653-374548654321```
   * [ ] Tenant ID (Active Directory ID). e.g. ```c73f8e89-005d-4cb5-8c90-82bead654321```
   * [ ] App ID (Client ID) for App Registration.  e.g ```3f546116-33c9-4b70-9186-250100654321```
   * [ ] Secret Key for App Registration. e.g. ```1HmMAz[PLyAm/u/9gW+V8xb33c654321```
* GCP project with Dome9-Connect service account. 
   * [ ] Create permissions for Dome9. [Manual](https://helpcenter.dome9.com/hc/en-us/articles/360003962974-Onboard-a-Google-Cloud-Project-to-Dome9) | [Script](https://github.com/Dome9/onboarding-scripts/tree/master/GCP) 
   * [ ] API Service Account credential key file in JSON format. e.g. ```mykey.json```

## Installation ##
1. Clone this repo into your local environment

```git clone https://github.com/Dome9/onboarding-scripts.git```

2. Navigate to the snapshot_asssessment directory:

```cd onboarding-scripts/snapshot_assessment```

3. [Get Dome9 V2 API id and secret key](https://secure.dome9.com/v2/settings/credentials).
   * Option 1: Set local environment variables ```d9id``` and ```d9secret``` with their respective values.
   * Option 2: Edit d9_account.conf and populate ```d9id``` and ```d9secret``` with their respective values.

## How to run ##
1. [Optional] Choose a Dome9 compliance ruleset (Default is NIST 800-53 Rev 4)
   * In Dome9, click **Compliance & Governance**  > **Rulesets**
   * Use the **Platform** filter on the left and choose a cloud provider.
   * In the right-pane, click on a **ruleset** from the list to open.
   * Look to the browser address bar. The ruleset id is the number in the URL following the last **forward slash**
     *  e.g. ```https://secure.dome9.com/v2/compliance-engine/policy/-2``` 
     * In this example, the ruleset id is ```-2```
2. In the console, navigate to the respective directory (`onboarding-scripts/snapshot_assessment`)
3. Run the script using a set mode <aws/azure/gcp> with the respective options. Below is the syntax with examples.
```
# Syntax
python3 snapshot_assessment.py [mode] [options] 
# Help with modes
python3 snapshot_assessment.py aws --help 
python3 snapshot_assessment.py azure --help 
python3 snapshot_assessment.py gcp --help 
#
# AWS Example
python3 snapshot_assessment.py aws --name testawsaccount --email user@domain.com --arn arn:aws:iam::012345678912:role/Dome9-Connect --externalid bkbj00xuTAM102IceF054321
# Azure Example
python3 snapshot_assessment.py azure --name testazureaccount --email user@domain.com --subscriptionid 7b7d6c48-c533-4a22-a653-374548654321 --tenantid c73f8e89-005d-4cb5-8c90-82bead654321 --appid 3f546116-33c9-4b70-9186-250100654321 --key 1HmMAz[PLyAm/u/9gW+V8xb33c654321
# GCP Example
python3 snapshot_assessment.py gcp --name testgcpaccount --email name@domain.com --keyfile ./mykey.json
```
### Command Line Modes ###
The mode indicates the public cloud provider type of the target account being assessed:
* ```aws``` : Amazon Web Services
* ```azure``` : Microsoft Azure
* ```gcp``` : Google Cloud Platform

### Command Line Options ###
Common Options
* ```--name``` : Friendly name of the cloud account (No spaces) (**required**)
* ```--email``` : E-mail address to send compliance report (**required**)
* ```--delay``` : Delay (in minutes) to wait for initial cloud account sync to complete. Default: ```10```. 

AWS Mode Options
* ```--arn``` : The role ARN of the AWS Dome9-Connect role (**required**)
* ```--externalid``` : The external ID used when creating the AWS Dome9-Connect role (**required**)
* ```--rulesetid``` : AWS-specific Dome9 Compliance Ruleset ID. Default: ```-16``` (NIST 800-53)

Azure Mode Options
* ```--subscriptionid``` : Azure Subscription ID (**required**)
* ```--tenandid``` : Azure AD/Tenant ID (**required**)
* ```--appid``` : Azure App (Client) ID for Dome9 App Registration (**required**)
* ```--key``` : Azure App (Client) Secret Key for Dome9 App Registration (**required**)
* ```--rulesetid``` : Azure-specific Dome9 Compliance Ruleset ID. Default: ```-23``` (NIST 800-53)

GCP Mode Options
* ```--keyfile``` : Path to GCP key file in JSON format of the Dome9 service account (**required**)
* ```--rulesetid``` : GCP-specific Dome9 Compliance Ruleset ID. Default: ```-25``` (NIST 800-53)

