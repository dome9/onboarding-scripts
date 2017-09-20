# Dome9-OnBoarding-CFT
CloudFormation Template that Prepare Role on AWS account to connenct to Dome9 


<u>The Process:<u>

## Dome9 Setup:
1. Log into Dome9 and go to 'Add AWS Account'
2. Select 'Get Started' for the mode you want (read or read/write)
3. Click 'Next' 
4. In the next window, copy down the string in the 'External ID' field. You'll need this later. 

## In AWS:
1. Choose file according to the protection mode you prefer (Read Only or Full Protect)
2. Create new CFT stack
3. Use the parameter "Externalid" from the onboarding process under "Create Role" step.
4.. No changes are needed in the Options menu.
5. Make sure you check "I acknowledge that AWS CloudFormation might create IAM resources." in the console or use "--capabilities CAPABILITY_IAM" in cli command. 
6. After the process finished, a new role is created which will contain the "role ARN" and the "External ID" that required to enter.

## Back in Dome9
1. Fill in the 'Display Name' field with a name for this account (ex: AWS-Prod) 
2. Paste in the Role ARN from the CloudFormation output
3. Click Finish



