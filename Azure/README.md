# Dome9 Azure Onboarding PowerShell Script

This script is for onboarding multiple subscriptions into Dome9 quickly. 

## Requirements
* Powershell v5 or newer which comes with Windows 10/2016
* OR
* Windows Management Framework 5.x. 
* Microsoft Online Services Sign-In Assistant for IT Professionals: https://www.microsoft.com/en-us/download/details.aspx?id=41950
* Install AzureRM PowerShell Module - Run: ```Install-Module -Name AzureRM -Confirm:$true```

## Once you have that at a minimum, the script works like this:

1. Script checks to see if the AzureRM AD Powershell modules are installed, and if not will exit the script and provide instructions on how to install them from the Powershell Gallery. Once all required modules are installed (minimum AzureRM.profile and AzureRM.Resources) it will proceed to Step 2.
 
2. Script requests user’s corporate credentials (email address and password) and logs into AzureRM
 
3. Script checks to see if an AD App was created using a name that at least starts with ‘Dome9’ and if it does, proceeds to Step 4. If the AD App does not exist, the script asks the user if it would like one created. If the user responds No, the script exits and explains the manual creation process. If the user responds Yes, it creates the AD App named Dome9-Connect, a SPN, and proceeds to Step 4.
 
4. Script asks the user if it would like to create an API Key for the Dome9-Connect AD Application. It also notes that if a key was already requested and saved to not request another. If the user responds Yes, it will create a new API Key and report it at the end of the script run. If the user responds No, it skips key creation and proceeds to Step 5.
 
5. Script begins to gather a list of all accessible subscriptions based on the user’s role access and stores then into a hash table. The table is presented to the user as a list of options. User is requested to select a single subscription option and hit enter, the selected subscription is connected to and proceeds to Step 6.
 
6. Script asks the user which Operation Mode to configure (Read-Only or Manage). If Read-Only is selected, the Dome9-Connect AD App is assigned Reader role access to the subscription. If Manage is selected, both Reader and Network Contributor role access is assigned to the subscription. If any errors are encountered or role access is already defined it will be reported to the console.
 
7. The final details are presented that can be used to plug into the fields in the Dome9 Azure Cloud Account add wizard to complete setup. If an application key was generated an additional NOTE will be presented to remind the user to save the key!

#### A big thanks to Mike Suter for putting this together!!!
 
