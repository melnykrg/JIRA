#!/usr/bin/env python
import requests, json
import os
from jira import JIRA
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

options = {'verify': False, 'server': 'https://jira.name.com'}
WORK_DIR = os.path.dirname(os.path.realpath(__file__))

CREDENTIAL_FILE = 'credentials.json'
with open(WORK_DIR + '/' + CREDENTIAL_FILE, 'r') as file:
    credential = json.load(file)
jira = JIRA(options, basic_auth=(credential["jira"]["username"], credential["jira"]['password']))
user_name = credential["jira"]["username"]
user_pass = credential["jira"]['password']

new_issue = jira.create_issue(project={'key': 'PROJECTNAME'},
                              summary='Test Summary',
                              description='Look into this one',
                              issuetype={'name': 'Incident'},
                              customfield_10321={'value': 'prod'})