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

DISCOVERY_URL = 'https://sheets.googleapis.com/v4/spreadsheets'
DRIVE_TOKEN = 'drive'
SPREADSHEET_TOKEN = 'spreadsheet'
PERMISSION_OPERATION = {
    'ADD': 'add',
    'REMOVE': 'remove',
    'SHOW': 'show',
}
PERMISSION_TYPES = {
    'DEFAULT': 'default',
    'SET_WRITER': 'set_writer',
    'SET_READER': 'set_reader',
    'SHARE_EVERYONE': 'share_everyone'
}


def nice_format(data):
    """Nice formatting output data

    :param data: <dict> - data to nice printing
    return: nice formatted data
    """
    return pprint.pformat(data, indent=4)


class SpreadsheetWorker:
    def __init__(self, client_secret_json, title='New SpreadSheet', app_name='Creating Google SpreadSheets'):
        self.SPREADSHEET_TITLE = title
        self.CLIENT_SECRET_FILE = client_secret_json
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
                flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.get_scope(token_type))
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

    def record_data(self, output_data, spreadsheet_id, sheet_range=None):
        """Record data to spreadsheet

        :param output_data: <list> - data for recording to Spreadsheet
        :param spreadsheet_id: <str> - id of modifying spreadsheet
        :param sheet_range: <str> - range of columns(Example - 'A3:B10').
        :return: <dict> - response from Google
        """
        token_type = SPREADSHEET_TOKEN
        ascii_number = 96  # number of last non alphabet digit in ASCII table, for setting a second part of table-range
        max_column = 0
        value_input_option = "USER_ENTERED"  # according to Google Sheets API manual:
        #  "The values will be parsed as if the user typed them into the UI"

        for i in xrange(len(output_data)):
            if max_column < len(output_data[i]):
                max_column = len(output_data[i])
        body = {
            'values': output_data
        }
        service = self.get_connection(token_type)
        if sheet_range:
            range_name = sheet_range
        else:
            range_begin = 'A1'
            range_name = range_begin + ':' + chr(ascii_number + max_column) + str(len(output_data))
        try:
            request = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range=range_name,
                valueInputOption=value_input_option, body=body
            ).execute()
            _logger.info('Data has received')
        except:
            _logger.error('Seems to be you pass invalid data. Please, check you input data and try again')
            request = None
        return request

    def create_spreadsheet(self):
        """Create empty spreadsheet

        :return: <str> - spreadsheet id
        """
        token_type = SPREADSHEET_TOKEN

        service = self.get_connection(token_type)
        request = service.spreadsheets().create(
            body={"properties":
                      {"title": self.SPREADSHEET_TITLE}
                  }
        ).execute()
        _logger.info('Response from Google: {}'.format(nice_format(request)))
        _logger.info('New spreadsheet with URL {} was created'.format(
            'https://docs.google.com/spreadsheets/d/' + request.get('spreadsheetId'))
        )
        return request.get('spreadsheetId')

    def get_spreadsheet_data(self, spreadsheet_id, sheet_name, sheet_range):
        """Get data from spreadsheet by sheet name and sheet range

        :param spreadsheet_id: <str> - id of modifying spreadsheet
        :param sheet_name: <str> - name of sheet from which the data will be taken
        :param sheet_range: <str> - range of columns(Example - 'A3:B10')
        :return: <list> - array of values from selected sheet in spreadsheet
        """
        token_type = SPREADSHEET_TOKEN
        range_body = str(sheet_name) + '!' + str(sheet_range)

        try:
            service = self.get_connection(token_type)
            request = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_body
            ).execute()
            values = request.get('values')
            _logger.info('Received values: {}'.format(nice_format(values)))
            return values
        except:
            _logger.error('Input Error. Try to check your input data.')
            return None

    def spreadsheet_constructor(self, output_data=None):
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
        try:
            spreadsheet_id = self.create_spreadsheet()
            if output_data:
                record = self.record_data(output_data, spreadsheet_id)
                _logger.info('Data was recorded. Response: {}'.format(nice_format(record)))
            return spreadsheet_id
        except:
            _logger.error('There was some error.. Please, check input data and try again')

    def set_permission_service(self, spreadsheet_id, token_type, permission_operation, body=None, permission_id=None):
        """
        If permission operation is adding new permission, then method send request to change permission
        for the selected spreadsheet.
        If permission operation is showing all permission, then method send request to get all permissions
        for the selected spreadsheet.

        :param spreadsheet_id: <str> - spreadsheet id
        :param token_type: <str> - expect 'drive' or 'spreadsheet' token type
        :param permission_operation: <str> - expect 'add', 'show' or 'remove'
        :param body: <dict> - properties of request
        :param permission_id: <str> - id of permission to delete(can get in from response of show_permission-method)
        :return: <dict> - response from Google
        """
        if permission_operation == PERMISSION_OPERATION['ADD']:
            service = self.get_connection(token_type)
            request = service.permissions().create(
                fileId=spreadsheet_id,
                sendNotificationEmail=False,
                body=body
            ).execute()
            return request

        elif permission_operation == PERMISSION_OPERATION['SHOW']:
            service = self.get_connection(token_type)
            request = service.permissions().list(
                fileId=spreadsheet_id,
                fields='permissions'
            ).execute()
            return request

        elif permission_operation == PERMISSION_OPERATION['REMOVE']:
            service = self.get_connection(token_type)
            request = service.permissions().delete(
                fileId=spreadsheet_id,
                permissionId=permission_id
            ).execute()
            return request

    def add_permission(self, spreadsheet_id, permission_type, user_email=None):
        """Add new permission to spreadsheet with id spreadsheet_id

        :param spreadsheet_id: <str> - spreadsheet id
        :param permission_type: <str> - type of permission, that apply to the spreadsheet
        :param user_email: <str> - email of user, to which is added permission
        :return: response or None
        """
        token_type = DRIVE_TOKEN
        try:
            permissions = {
                'access_by_link': {
                    'type': 'anyone',
                    'role': 'reader'
                },
                'set_writer': {
                    'type': 'user',
                    'role': 'writer',
                    'emailAddress': user_email
                },
                'set_reader': {
                    'type': 'user',
                    'role': 'reader',
                    'emailAddress': user_email
                },
                'share_everyone': {
                    'type': 'anyone',
                    'role': 'writer',
                }
            }
            response = None

            if permission_type != PERMISSION_TYPES['SHARE_EVERYONE'] and \
                            permission_type != PERMISSION_TYPES['DEFAULT']:
                if user_email:
                    if permission_type == PERMISSION_TYPES['SET_READER']:
                        request = self.set_permission_service(
                            spreadsheet_id,
                            token_type,
                            PERMISSION_OPERATION['ADD'],
                            permissions['set_reader']
                        )
                        response = request
                    elif permission_type == PERMISSION_TYPES['SET_WRITER']:
                        request = self.set_permission_service(
                            spreadsheet_id,
                            token_type,
                            PERMISSION_OPERATION['ADD'],
                            permissions['set_writer']
                        )
                        response = request
                else:
                    self.email_error()
            elif permission_type == PERMISSION_TYPES['SHARE_EVERYONE']:
                request = self.set_permission_service(
                    spreadsheet_id,
                    token_type,
                    PERMISSION_OPERATION['ADD'],
                    permissions['share_everyone']
                )
                response = request
            elif permission_type == PERMISSION_TYPES['DEFAULT']:
                request = self.set_permission_service(
                    spreadsheet_id,
                    token_type,
                    PERMISSION_OPERATION['ADD'],
                    permissions['access_by_link']
                )
                response = request
            else:
                self.input_error()
            _logger.info('Received response {}'.format(nice_format(response)))
            return response
        except:
            _logger.error('Invalid data. Please, check the input data')
            return None

    def show_permissions(self, spreadsheet_id):
        """Show all permissions of selected spreadsheet (with id spreadsheet_id)
        :param spreadsheet_id: <str> - spreadsheet id
        :return: <dict> - permissions
        """
        token_type = DRIVE_TOKEN
        try:
            response = self.set_permission_service(spreadsheet_id, token_type, PERMISSION_OPERATION['SHOW'])
            spreadsheet_permissions = response['permissions']
            _logger.info('Received response {}'.format(nice_format(spreadsheet_permissions)))
            return spreadsheet_permissions
        except:
            _logger.error('Invalid data. Please, check the input data')
            return None

    def remove_permission(self, spreadsheet_id, permission_id):
        """Remove permission by id of permission
        :param spreadsheet_id: <str> - spreadsheet id
        :param permission_id: <str> - id of permission to delete(can get in from response of show_permission-method)
        :return: ''
        """
        token_type = DRIVE_TOKEN
        try:
            response = self.set_permission_service(
                spreadsheet_id,
                token_type,
                PERMISSION_OPERATION['REMOVE'],
                permission_id=permission_id)
            _logger.info('Received response {}'.format(nice_format(response)))
            return response
        except:
            _logger.error('Invalid data. Please, check the input data')
            return None

    def email_error(self):
        return _logger.error('User email is not defined.')

    def input_error(self):
        return _logger.error('Input data is not valid.')
