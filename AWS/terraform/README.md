# Dome9-OnBoarding-Terraform
Terraform Templates that Prepare the Role on AWS account to connenct to Dome9 

# Steps:

## Dome9 Setup:
1. Log into Dome9 and go to 'Add AWS Account'
2. Select 'Get Started' for the mode you want (read or read/write)
3. Click 'Next' 
4. In the next window, copy down the string in the 'External ID' field. You'll need this later. 

## In Terraform:
1. Choose file according to the protection mode you prefer (Read Only or Full Protect)
2. Remove or rename the .tf file you won't be using since Terraform will try to run all *.tf files in the directory.
3. Run 'terraform plan'
4. If this looks good, run 'terraform apply'
5. Put in the External ID when prompted from the Dome9 setup steps
6. After the process finished, a new role is created which will contain the "Role ARN".

## Back in Dome9:
1. Fill in the 'Display Name' field with a name for this account (ex: AWS-Prod) 
2. Paste in the Role ARN from the Terraform output
3. Click Finish



