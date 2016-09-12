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

CLIENT_SECRET_FILE = 'client_secret.json'


def nice_format(data):
    """Nice formatting output data

    :param data: <dict> - data to nice printing
    return: nice formatted data
    """
    return pprint.pformat(data, indent=4)


class SpreadsheetWorker:
    def __init__(self, title, app_name='Creating Google SpreadSheets'):
        self.APPLICATION_NAME = app_name
        self.SPREADSHEET_TITLE = title
        self.DISCOVERY_URL = 'https://sheets.googleapis.com/v4/spreadsheets'

    def credentials_path_composer(self, token_type):
        """
        Get user credentials from ~/PROJECT_NAME/worker/.credentials, if they present(created before) or create new
        directory .credentials ~/PROJECT_NAME/worker/
        :param token_type: <string> - expect 'drive' or 'spreadsheet' token type
        :return: credential_path, if token type is correct, else return None
        """
        home_dir = os.getcwd()
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        if token_type == 'drive':
            credential_path = os.path.join(credential_dir, 'google-drive-token.json')
            return credential_path
        elif token_type == 'spreadsheet':
            credential_path = os.path.join(credential_dir, 'google-spreadsheet-token.json')
            return credential_path
        else:
            return None

    def get_scope(self, token_type):
        scope = None
        if token_type == 'drive':
            scope = 'https://www.googleapis.com/auth/drive'
        elif token_type == 'spreadsheet':
            scope = 'https://www.googleapis.com/auth/spreadsheets'

        return scope

    def get_credentials(self, token_type):
        """
        Gets valid user credentials
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        :param self:
        :param token_type: <string> - expect 'drive' or 'spreadsheet' token type
        :return: Credentials, the obtained credential.
        """

        credential_path = self.credentials_path_composer(token_type)
        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, self.get_scope(token_type))
            flow.user_agent = self.APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            _logger.warning('Storing credentials to ' + credential_path)
        return credentials

    def create_spreadsheet(self):
        """Create new Google Spreadsheet
        :return: new spreadsheet id
        Creates a Sheets API service object and new spreadsheet with and return id of created sheet
        """
        token_type = 'spreadsheet'
        credentials = self.get_credentials(token_type)
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=self.DISCOVERY_URL)
        response = service.spreadsheets().create(body={"properties": {"title": self.SPREADSHEET_TITLE}}).execute()

        _logger.warning(nice_format(response))

        return response.get('spreadsheetId')
