# **Add multiple GCP projects (from one organization)** #
A command line tool to add multiple all projects (from one organization) into Dome9 ARC platform.<br/>
This tool assume a single GCP service account with its credentials file donwloaded.


## Requirements ##
* NodeJs stable version 4.3.2 or later.
( Can be Download <a href="https://nodejs.org">here</a> )
* GCP service Account key with permissions for the relevant projects.
* <a href="https://github.com/Dome9/V2_API/blob/master/README.md">Dome9 V2 API key</a>.

## Installation ##
1 Clone this repo into your local machine

```git clone https://github.com/Dome9/onboarding-scripts.git```

2 Navigate to this tool folder:

```cd onboarding-scripts/GCP```

3 Install the tool's dependencies and register it:

```npm install```

## How to run ##
1. Using console, navigate to this tools directory (`onboarding-scripts/GCP`)
2. Run the command ```node gcpOrgImporter.js --help``` to understand the command line arguments.

### Command Line arguments ###
* -p or --path : Path to the JSON file with the service account key (**required**).
* -i or --id : The id of Dome9 API key (**required**).
* -s or --secret : Dome9 API key's secret(**required**).
