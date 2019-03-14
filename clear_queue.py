#!/usr/bin/env python
import requests, json
import urllib2
import base64
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from jira import JIRA

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Jira():
    def __init__(self):
        options = {'verify': False, 'server': 'https://jira.test.com'}  # Options to connect to JIRA
        WORK_DIR = os.path.dirname(os.path.realpath(__file__))
        CREDENTIAL_FILE = 'credentials.json'
        with open(WORK_DIR + '/' + CREDENTIAL_FILE, 'r') as file:
            credential = json.load(file)
        self.jira = JIRA(options, basic_auth=(credential["jira"]["username"], credential["jira"]['password']))
        self.user_name = credential["jira"]["username"]
        self.user_pass = credential["jira"]['password']
        self.jira_filter = self.jira.search_issues(
    'project="TEAMNAME: Platform Operations" and reporter=nagios and resolution=Unresolved', maxResults=1000)
        self.jira_filter_for_not_updated = self.jira.search_issues(
    'project = TEAMNAME AND resolution = Unresolved AND updated <= -1w AND assignee in (nagios)', maxResults=1000)

    def assign_and_investigate(self, issue):
        url = 'https://jira.test.com/rest/api/2/issue/%s/transitions' % issue.key
        auth = base64.encodestring('%s:%s' % (self.user_name, self.user_pass)).replace('\n', '')

        data = json.dumps({
            'transition': {
                'id': 11
            }})

        request = urllib2.Request(url, data, {
            'Authorization': 'Basic %s' % auth,
            'Content-Type': 'application/json',
        })
        print urllib2.urlopen(request).read()

    def resolve_ticket(self, issue):
        url = 'https://jira.test.com/rest/api/2/issue/%s/transitions' % issue.key
        auth = base64.encodestring('%s:%s' % (self.user_name, self.user_pass)).replace('\n', '')
        issue.fields.labels.append(u'auto_closed')
        issue.update(fields={"labels": issue.fields.labels})

        data = json.dumps({
            'transition': {
                'id': 71
            },
            'fields': {
                'resolution': {"name": "Self Corrected"}
            }})
        request = urllib2.Request(url, data, {
            'Authorization': 'Basic %s' % auth,
            'Content-Type': 'application/json',
        })
        print urllib2.urlopen(request).read()

    def get_status_by_comment(self, issue):
        if len(self.jira.comments(issue)) > 0:
            last_comment = ""
            for comment in self.jira.comments(issue):

                if str(comment.author) == 'Monitoring':
                    last_comment = comment.body
                else:
                    return False
            status = last_comment.split("*")[6].split()[0]
            if status == "RECOVERY":
                return True
            else:
                return False
        else:
            return False

if __name__ == '__main__':
    my_jira = Jira()

    for issue in my_jira.jira_filter_for_not_updated:
        print issue
        try:
            my_jira.assign_and_investigate(issue)
            my_jira.resolve_ticket(issue)
        except:
            print "Unable to close"
    for issue in my_jira.jira_filter:
        print issue
        if my_jira.get_status_by_comment(issue):
            try:
                my_jira.assign_and_investigate(issue)
                my_jira.resolve_ticket(issue)
            except:
                print "Unable to close"
