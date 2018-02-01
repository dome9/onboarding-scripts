<#
.NOTES
	Author: Mike Suter 
	Contact: mike.suter@cbre.com
	Version: 1.0.3
	Date: 2017.09.08
	Title: Azure RM Script - Gathers Azure Account Data for addition of Cloud Account to Dome9
	Rights: Written for Dome9 Security Ltd. for use as is or modified, all rights for free.
.SYNOPSIS
	Connects to AzureRM, offers menu of Subscriptions and presents data needed for Dome9 connectivity. Supports MFA Auth.
.DESCRIPTION
	Script requests the users corporate SSO credentials (email address and password) then logs into AzureRM.
	A menu of available subscriptions is presented based on the account's role access. Once a subscription
	is selected, a new Key is generated, and all of the data required to add the Azure Account to Dome9 will be presented.
.EXAMPLE
	- Run the script from the powershell console
.PREREQUISITES
	- Windows PowerShell 5.0
	- Microsoft Online Services Sign-In Assistant for IT Professionals:	https://www.microsoft.com/en-us/download/details.aspx?id=41950
	- Install AzureRM PowerShell Module - Run: Install-Module -Name AzureRM -Confirm:$true
#>

## Function to ask to create an Azure AD Application automatically
Function Create-Dome9ConnectAdApp {
	Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host "Create an AD Application named Dome9-Connect " -Foregroundcolor White -NoNewline
	Write-Host '[' -Foregroundcolor White -NoNewLine; Write-Host "n" -Foregroundcolor Green -NoNewLine
	Write-Host '/' -Foregroundcolor White -NoNewLine; Write-Host 'Y' -Foregroundcolor Green -NoNewLine
	Write-Host '] ?' -Foregroundcolor White -NoNewLine; Write-Host ' :> ' -NoNewline -ForegroundColor DarkGray; Read-Host
}

## Function to ask to create an Azure AD Application API Key
Function Create-Dome9ConnectAdAppApiKey {
	
	Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host "Create an AD Application API Key " -Foregroundcolor White
	Write-Host 'NOTE: ' -Foregroundcolor DarkCyan -NoNewline; Write-Host 'If you have already created and saved a key select ' -Foregroundcolor White -NoNewLine
	Write-Host 'N' -Foregroundcolor Yellow; Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'Create Key ' -ForegroundColor White -NoNewline
	Write-Host '[' -Foregroundcolor White -NoNewLine; Write-Host "n" -Foregroundcolor Green -NoNewLine
	Write-Host '/' -Foregroundcolor White -NoNewLine; Write-Host 'Y' -Foregroundcolor Green -NoNewLine
	Write-Host '] ?' -Foregroundcolor White -NoNewLine; Write-Host ' :> ' -NoNewline -ForegroundColor DarkGray; Read-Host
	Write-Host `n -NoNewline
}

## Function to ask which Operation Mode to configure
Function Select-Dome9OperationMode {
	Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host "Please select the Operation Mode " -Foregroundcolor White -NoNewline
	Write-Host '[' -Foregroundcolor White -NoNewLine; Write-Host "R" -Foregroundcolor Green -NoNewLine; Write-Host 'ead-Only' -NoNewline -ForegroundColor White
	Write-Host '/' -Foregroundcolor White -NoNewLine; Write-Host 'M' -Foregroundcolor Green -NoNewLine; Write-Host 'anage' -NoNewline -ForegroundColor White
	Write-Host '] ?' -Foregroundcolor White -NoNewLine; Write-Host ' :> ' -NoNewline -ForegroundColor DarkGray; Read-Host
}

#### AES Encryption Function provided by ctigeek @ GitHub: https://gist.github.com/ctigeek/2a56648b923d198a6e60
function Create-AesManagedObject($key, $IV) {

    $aesManaged = New-Object "System.Security.Cryptography.AesManaged"
    $aesManaged.Mode = [System.Security.Cryptography.CipherMode]::CBC
    $aesManaged.Padding = [System.Security.Cryptography.PaddingMode]::Zeros
    $aesManaged.BlockSize = 128
    $aesManaged.KeySize = 256

    if ($IV) {
        if ($IV.getType().Name -eq "String") {
            $aesManaged.IV = [System.Convert]::FromBase64String($IV)
        }
        else {
            $aesManaged.IV = $IV
        }
    }

    if ($key) {
        if ($key.getType().Name -eq "String") {
            $aesManaged.Key = [System.Convert]::FromBase64String($key)
        }
        else {
            $aesManaged.Key = $key
        }
    }

    $aesManaged
}

#### Create 44-char key Function provided by ctigeek @ GitHub: https://gist.github.com/ctigeek/2a56648b923d198a6e60
function Create-AesKey() {
    $aesManaged = Create-AesManagedObject 
    $aesManaged.GenerateKey()
    [System.Convert]::ToBase64String($aesManaged.Key)
}

######## BEGIN SCRIPT PROCESSING ########
[console]::BackgroundColor = 'Black'
Clear
Write-Host ('#' * ("# Executing Script $($MyInvocation.MyCommand.Path)").Length + '##') -Foregroundcolor DarkGray
Write-Host '#' -Foregroundcolor DarkGray -NoNewLine; Write-Host ' Executing Script ' -Foregroundcolor White -NoNewLine
Write-Host $MyInvocation.MyCommand.Path -Foregroundcolor Cyan -NoNewLine; Write-Host ' #' -Foregroundcolor DarkGray
Write-Host ('#' * ("# Executing Script $($MyInvocation.MyCommand.Path)").Length + '##') -Foregroundcolor DarkGray
Write `r

## Checks to see if the AzureRM Powershell Modules are installed
Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host "Checking if AzureRM Powershell modules are installed..." -NoNewline -ForegroundColor White
If (!(Get-Module -ListAvailable -Name AzureRM.profile)) {$isAzureRmProfInstalled=$false} Else {$isAzureRmProfInstalled=$true}
If (!(Get-Module -ListAvailable -Name AzureRM.Resources)) {$isAzureRmResInstalled=$false} Else {$isAzureRmResInstalled=$true}

## If neither AzureRM.profile nor AzureRM.Resources are installed, output error message and exit
If (!$isAzureRmProfInstalled -and !$isAzureRmResInstalled) {
	Write-Host "Failed" -ForegroundColor Red; Write-Host `n -NoNewline
	Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'MISSING ' -Foregroundcolor Red -NoNewline;
	Write-Host 'AzureRM.profile Powershell Module is not installed.' -ForegroundColor Yellow
	Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'MISSING ' -Foregroundcolor Red -NoNewline;
	Write-Host 'AzureRM.Resources Powershell Module is not installed.' -ForegroundColor Yellow; Write-Host '## ' -Foregroundcolor DarkGray
	Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'Please execute ' -ForegroundColor White -NoNewline
	Write-Host 'Install-Module -Name AzureRM -Confirm:$true ' -ForegroundColor Green -NoNewline; Write-Host 'from your Powershell console.' -ForegroundColor White
	Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'Run the Dome9 script again.' -ForegroundColor White
	exit
	## If AzureRM.profile is not installed, output error message and exit
} ElseIf (!$isAzureRmProfInstalled) {
		Write-Host "Failed" -ForegroundColor Red; Write-Host `n -NoNewline
		Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'MISSING ' -Foregroundcolor Red -NoNewline;
		Write-Host 'AzureRM.profile Powershell Module is not installed.' -ForegroundColor Yellow
		Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'Please execute ' -ForegroundColor White -NoNewline
		Write-Host 'Install-Module -Name AzureRM -Confirm:$true ' -ForegroundColor Green -NoNewline; Write-Host 'from your Powershell console.' -ForegroundColor White
		Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'Run the Dome9 script again.' -ForegroundColor White
		exit
		## If AzureRM.Resources is not installed, output error message and exit
	} ElseIf (!$isAzureRmResInstalled) {
			Write-Host "Failed" -ForegroundColor Red; Write-Host `n -NoNewline
			Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'MISSING ' -Foregroundcolor Red -NoNewline;
			Write-Host 'AzureRM.Resources Powershell Module is not installed.' -ForegroundColor Yellow
			Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'Please execute ' -ForegroundColor White -NoNewline
			Write-Host 'Install-Module -Name AzureRM -Confirm:$true ' -ForegroundColor Green -NoNewline; Write-Host 'from your Powershell console.' -ForegroundColor White
			Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'Run the Dome9 script again.' -ForegroundColor White
			exit
		}
## If all modules are installed reports success
Write-Host "Done" -ForegroundColor Green; Write-Host `n -NoNewline

## Requests SSO credentials from user and logs into AzureRM Portal

## Login Prompt
## Required install Microsoft Online Services Sign-In Assistant for IT Professionals RTW
##	https://www.microsoft.com/en-us/download/details.aspx?id=41950
Login-AzureRmAccount

## Checks to see if the AD Application was created with the correct name
Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host "Checking if Dome9-Connect Azure AD Application was created..." -NoNewline -ForegroundColor White
If (!(Get-AzureRmADApplication -DisplayNameStartWith 'Dome9')) {
	Write-Host "Missing" -ForegroundColor Red; Write-Host `n -NoNewline
	
	## Ask to include Resource Groups at entity location
	:CreateDome9ConnectAdApp Do {
		Switch (Create-Dome9ConnectAdApp) {
			'Y' {
				$createDome9AdApp = $true
				Break CreateDome9ConnectAdApp
			}
			'N' {
				$createDome9AdApp = $false
				Break CreateDome9ConnectAdApp
			}
			default {Write-Warning 'Invalid Choice. Try again.'}
		}
	} While ($true)

	If ($createDome9AdApp) {
		## Creating new AD Application
		Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host "Creating new AD Application..." -NoNewline -ForegroundColor White
		$newguid = [guid]::NewGuid()
		$identifierUris = 'https://XXX.onmicrosoft.com/' + $newguid
		New-AzureRmADApplication -DisplayName 'Dome9-Connect' -HomePage 'https://secure.dome9.com' -IdentifierUris $identifierUris | Out-Null
		$AdAppId = (Get-AzureRmADApplication -DisplayNameStartWith 'Dome9').ApplicationId.ToString()
		$AdAppObjectId = (Get-AzureRmADApplication -DisplayNameStartWith 'Dome9').ObjectId.ToString()
		Write-Host "Done" -ForegroundColor Green

		#Create new SPN for the AD Application
		Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host "Creating a new SPN for the AD Application..." -NoNewline -ForegroundColor White
		$SPN = New-AzureRmADServicePrincipal -ApplicationId $AdAppId
		$spnName = $SPN.ServicePrincipalNames
		Write-Host "Done" -ForegroundColor Green; Write-Host `n -NoNewline
	} Else {
			## Not creating new AD Application
			Write-Host `n -NoNewline; Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'MISSING ' -Foregroundcolor Red -NoNewline;
			Write-Host "Azure AD Application with Name starting with 'Dome9' doesn't exist." -ForegroundColor Yellow
			Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host "Please create an AD Application with a name that at least starts with " -NoNewline -ForegroundColor White
			Write-Host "'Dome9' " -ForegroundColor Green; Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine
			Write-Host 'and run the script again.' -ForegroundColor White
			exit
		}
} Else {
		$AdAppId = (Get-AzureRmADApplication -DisplayNameStartWith 'Dome9').ApplicationId.ToString()
		$AdAppObjectId = (Get-AzureRmADApplication -DisplayNameStartWith 'Dome9').ObjectId.ToString()
		Write-Host "Done" -ForegroundColor Green; Write-Host `n -NoNewline
	}

	## Ask to create a new AD Application API Key
	:CreateDome9ConnectAdAppApiKey Do {
		Switch (Create-Dome9ConnectAdAppApiKey) {
			'Y' {
				$CreateDome9AdAppApiKey = $true
				Break CreateDome9ConnectAdAppApiKey
			}
			'N' {
				$CreateDome9AdAppApiKey = $false
				Break CreateDome9ConnectAdAppApiKey
			}
			default {Write-Warning 'Invalid Choice. Try again.'}
		}
	} While ($true)
	
If ($CreateDome9AdAppApiKey) {
## Creating new API Key on the Dome9-Connect AD Application
Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host "Creating new AD Application API Key (44-char length, 2 year duration)..." -NoNewline -ForegroundColor White
$AdAppApiKey = Create-AesKey
$secureAdAppApiKey = ConvertTo-SecureString -String $AdAppApiKey -AsPlainText -Force
New-AzureRmADAppCredential -ObjectId $AdAppObjectId -Password $secureAdAppApiKey -EndDate ((Get-Date).AddYears(2)) | Out-Null
Write-Host "Done" -ForegroundColor Green; Write-Host `n -NoNewline
} Else {$AdAppApiKey = '<Use previously generated key>'}

## Begin subscription gathering for selection
Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'Please select a ' -Foregroundcolor White -NoNewLine
Write-Host 'Subscription ' -Foregroundcolor Yellow -NoNewLine; Write-Host 'to gather details from' -Foregroundcolor White -NoNewLine

## Gather Subscription options and store in a hash table
$SubDetails = @()
$Details = @{}
$SubIndex = 0
$Subs = Get-AzureRmSubscription -WarningAction 0 | % {
	$Details = [PSCustomObject]@{'Option' = $SubIndex;'Subscription Id' = $_.Id;'Subcription Name' = $_.Name}
	$SubDetails += $Details
	$SubIndex++
}

## If there are more than one Subscriptions available, presents a list of Subs and requests a selection
If ($SubDetails.Length -ne 1) {
	$SubDetails | ft -AutoSize @{n='Option';e={$_.Option};Alignment='left'}, 'Subscription Id', 'Subcription Name'
	Write-Host '# ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'Please select only one ' -Foregroundcolor White -NoNewLine
	Write-Host 'Subscription ' -Foregroundcolor Yellow -NoNewLine;Write-Host 'from the list of Options' -Foregroundcolor White
	Write-Host 'Option' -Foregroundcolor White -NoNewLine; Write-Host ' :> ' -NoNewline -ForegroundColor DarkGray; $SubOption = Read-Host; Write `r
	$Sub = $SubDetails[$SubOption].'Subcription Name'
} Else {$Sub = $SubDetails[0].'Subcription Name'}

Write-Host -Foregroundcolor Cyan "Subscription $Sub is being used for the Data Set.
	"
Write-Host ' ## Connecting to Subscription...' -ForegroundColor DarkCyan -NoNewLine
Select-AzureRmSubscription -SubscriptionName $Sub | Out-Null
$Subscription = Get-AzureRmSubscription -SubscriptionName $Sub -WarningAction 0 | Sort Name
$SubName = $Subscription.Name
$SubId = $Subscription.Id
Write-Host 'Done!' -Foregroundcolor Green; Write-Host `n -NoNewline

	## Ask to select the Dome9 Operation Mode (Read-Only or Manage)
	:SelectDome9OperationMode Do {
		Switch (Select-Dome9OperationMode) {
			'R' {
				$SelectDome9OperationMode = 'ReadOnly'
				Break SelectDome9OperationMode
			}
			'M' {
				$SelectDome9OperationMode = 'Manage'
				Break SelectDome9OperationMode
			}
			default {Write-Warning 'Invalid Choice. Try again.'}
		}
	} While ($true)

## Assigning Reader Role access to the Dome9-Connect AD Application at scope Subscription
Write-Host `n -NoNewline; Write-Host " ## Assigning Reader Role access to the Dome9-Connect AD App at sub $SubName..." -NoNewline -ForegroundColor DarkCyan
$Scope = '/subscriptions/' + $SubId

$ErrorActionPreference = 'Stop'
	Try {
		New-AzureRmRoleAssignment -ServicePrincipalName $AdAppId -RoleDefinitionName Reader -Scope $Scope | Out-Null
	} Catch [exception] {Write-Host "$_ " -NoNewline}
	Finally {Write-Host "Done" -ForegroundColor Green}
$ErrorActionPreference = 'Continue'

## If Manage Operation Mode selected, also assigning Network Contributor Role access to the Dome9-Connect AD Application at scope Subscription
If ($SelectDome9OperationMode -eq 'Manage') {
	## Assigning Network Contributor Role access to the Dome9-Connect AD Application at scope Subscription
	Write-Host " ## Assigning Network Contributor Role access to the Dome9-Connect AD App at sub $SubName..." -NoNewline -ForegroundColor DarkCyan
	$Scope = '/subscriptions/' + $SubId

	$ErrorActionPreference = 'Stop'
		Try {
			New-AzureRmRoleAssignment -ServicePrincipalName $AdAppId -RoleDefinitionName 'Network Contributor' -Scope $Scope | Out-Null
		} Catch [exception] {Write-Host "$_ " -NoNewline}
		Finally {Write-Host "Done" -ForegroundColor Green}
	$ErrorActionPreference = 'Continue'
}
Write-Host `n -NoNewline

$SubDetails = @()
$Details = @{}
$Details = [PSCustomObject]@{
	'Application ID' = $AdAppId
	'Application Key' = $AdAppApiKey
	'Active Directory ID' = $Subscription.TenantId
	'Subscription ID' = $SubId
	'Display Name' = 'Azure ' + $SubName
}

## Write the final information to the console for use with Dome9 configuration
Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host "Use the Azure Subscription " -Foregroundcolor White -NoNewLine
Write-Host "$SubName " -ForegroundColor Green -NoNewline; Write-Host "details below to add a new Cloud Account to Dome9" -ForegroundColor White

If ($AdAppApiKey -ne '<Use previously generated key>') { 
	Write-Host '## ' -Foregroundcolor DarkGray -NoNewLine; Write-Host 'NOTE: ' -Foregroundcolor DarkCyan -NoNewline; Write-Host 'Please save the ' -NoNewline -ForegroundColor White
	Write-Host "Application Key " -ForegroundColor Green -NoNewline; Write-Host 'as it will be needed again for adding additional Azure subscriptions to Dome9.' -Foregroundcolor White
}

$Details