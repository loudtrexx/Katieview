import subprocess
import json

def configcreate():
    """Create a configuration file with default values."""
    global config_data
    with open('config.json', 'w') as config_file:
        json.dump(config_data, config_file, indent=4)
    print("Configuration file created successfully.")
    # Optionally, run the updater after creating the config
  #  subprocess.run(['python', 'main.py']) # Assume user is on windows. Linux and Windows seperating check coming at some point. Right now unused.

def configdatasurvey():
    global config_data
    repo = input("Enter the GitHub repository in format user/repository: ") # e.g., "loudtrexx/katieview"
    config_data = {
        "repo": repo
    }

configdatasurvey()
configcreate()