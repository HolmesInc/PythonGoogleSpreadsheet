import httplib2
from apiclient import discovery
import oauth2client
from oauth2client import client, tools

import os
import pprint
import logging as _logger

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/google-spreadsheet-token.json'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Creating Google Sheets'    
SPREADSHEET_TITLE = 'Sheet title'


def nice_format(data):
    """Nice formatting output data

    :param data: <dict> - data to nice printing
    return: nice formatted data
    """
    return pprint.pformat(data, indent=4)


def get_credentials():
    """Gets valid user credentials

    Get user credentials from ~/PROJECT_NAME/.credentials, if they present(created before)

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    return: Credentials, the obtained credential.
    """
    home_dir = os.getcwd()
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'google-spreadsheet-token.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        _logger.warning('Storing credentials to ' + credential_path)
    return credentials


def create_spreadsheet():
    """Create new Google Spreadsheet

    return: new spreadsheet id

    Creates a Sheets API service object and new spreadsheet with and return id of created sheet
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    discoveryUrl = ('https://sheets.googleapis.com/v4/spreadsheets')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    result = service.spreadsheets().create(body={"properties": {"title": SPREADSHEET_TITLE}}).execute()

    _logger.warning(nice_format(result))


if __name__ == '__main__':
    create_spreadsheet()