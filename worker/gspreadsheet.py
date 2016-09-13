import httplib2
from apiclient import discovery
import oauth2client
from oauth2client import client, tools

import os
import pprint
import logging as _logger

_logger.getLogger().setLevel(_logger.INFO)

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

CLIENT_SECRET_FILE = 'client_secret.json'
DISCOVERY_URL = 'https://sheets.googleapis.com/v4/spreadsheets'
DRIVE_TOKEN = 'drive'
SPREADSHEET_TOKEN = 'spreadsheet'


def nice_format(data):
    """Nice formatting output data

    :param data: <dict> - data to nice printing
    return: nice formatted data
    """
    return pprint.pformat(data, indent=4)


class SpreadsheetWorker:
    def __init__(self, title='New SpreadSheet', app_name='Creating Google SpreadSheets'):
        self.SPREADSHEET_TITLE = title
        self.APPLICATION_NAME = app_name

    def credentials_path_composer(self, token_type):
        """
        Get user credentials from ~/PROJECT_NAME/worker/.credentials, if they present(created before) or create new
        directory .credentials ~/PROJECT_NAME/worker/ with a credentials

        :param token_type: <str> - expect 'drive' or 'spreadsheet' token type
        :return: credential_path, if token type is correct, else return None
        """
        home_dir = os.getcwd()
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        if token_type == DRIVE_TOKEN:
            credential_path = os.path.join(credential_dir, 'google-drive-token.json')
            return credential_path
        elif token_type == SPREADSHEET_TOKEN:
            credential_path = os.path.join(credential_dir, 'google-spreadsheet-token.json')
            return credential_path
        else:
            return None

    def get_scope(self, token_type):
        """Select scope for request to Spreadsheet API or to Drive API

        :param token_type: <str> - expect 'drive' or 'spreadsheet' token type
        :return: <str> - url
        """
        scope = None
        if token_type == DRIVE_TOKEN:
            scope = 'https://www.googleapis.com/auth/drive'
        elif token_type == SPREADSHEET_TOKEN:
            scope = 'https://www.googleapis.com/auth/spreadsheets'
        return scope

    def get_credentials(self, token_type):
        """Gets valid user credentials
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        :param token_type: <str> - expect 'drive' or 'spreadsheet' token type
        :return: Credentials, the obtained credential.
        """
        credential_path = self.credentials_path_composer(token_type)
        if credential_path:
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
        else:
            return None

    def get_connection(self, token_type):
        """Creates a Sheets API service object
        :param token_type: <str> - expect 'drive' or 'spreadsheet' token type
        :return: <object> - Sheets API service object
        """
        credentials = self.get_credentials(token_type)
        http = credentials.authorize(httplib2.Http())
        service = None
        if token_type == SPREADSHEET_TOKEN:
            service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URL)
        elif token_type == DRIVE_TOKEN:
            service = discovery.build('drive', 'v3', http=http)
        return service

    def record_data(self, output_data, spreadsheet_id):
        """Record data to spreadsheet

        :param output_data: <list> - data for recording to Spreadsheet
        :param spreadsheet_id: <str> - id of modifying spreadsheet
        :return: <dict> - response from Google
        """
        token_type = SPREADSHEET_TOKEN
        ascii_number = 96  # number of last non alphabet digit in ASCII table, for setting a second part of table-range
        max_column = 0
        range_begin = 'A1'
        value_input_option = "USER_ENTERED"  # according to Google Sheets API manual:
        #  "The values will be parsed as if the user typed them into the UI"

        for i in xrange(len(output_data)):
            if max_column < len(output_data[i]):
                max_column = len(output_data[i])
        body = {
            'values': output_data
        }
        range_name = range_begin + ':' + chr(ascii_number + max_column) + str(len(output_data))
        print range_name

        service = self.get_connection(token_type)
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body
        ).execute()
        return result

    def construct_spreadsheet(self):
        """Create empty spreadsheet

        :return: <str> - spreadsheet id
        """
        token_type = SPREADSHEET_TOKEN
        credentials = self.get_credentials(token_type)
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URL)
        response = service.spreadsheets().create(body={"properties": {"title": self.SPREADSHEET_TITLE}}).execute()
        _logger.info('Response from Google: {}'.format(nice_format(response)))
        _logger.info('New spreadsheet with URL {} was created'.format(
            'https://docs.google.com/spreadsheets/d/' + response.get('spreadsheetId'))
        )
        return response.get('spreadsheetId')

    def create_spreadsheet(self, output_data=None):
        """Create new Google Spreadsheet
        If output_data not define, spreadsheet generator create new empty spreadsheet with access
        permission only for user, who allowed using his data for app (in browser)
        Else create new spreadsheet with access permission only for user, who allowed using his data for app
        (in browser) and data from output_data

        :param output_data: <list> - data for recording to Spreadsheet
        example:
        output_data = [
            ['Iron Man', 'Tony Stark'],
            [43, 1.75, 80],
            ['Just like his costume;-]']
        ]
        :return: new spreadsheet id
        """
        if output_data:
            spreadsheet_id = self.construct_spreadsheet()
            record = self.record_data(output_data, spreadsheet_id)
            _logger.info('Data was recorded. Response: {}'.format(nice_format(record)))
        else:
            self.construct_spreadsheet()






