import httplib2
from apiclient import discovery
import oauth2client
from oauth2client import client, tools
from oauth2client.service_account import ServiceAccountCredentials

import pprint
import logging

_logger = logging.getLogger('PySpreadsheet')
_logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)s.%(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
_logger.addHandler(ch)

_DISCOVERY_URL = 'https://sheets.googleapis.com/v4/spreadsheets'
_DRIVE_TOKEN = 'drive'
_SPREADSHEET_TOKEN = 'spreadsheet'
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


def _nice_format(data):
    """ Output data formatter

    :param data: - data to formatting
    return: formatted data
    """
    return pprint.pformat(data, indent=4)


class SpreadsheetWorker:
    def __init__(self, client_secret_json, title='New SpreadSheet', app_name='Creating Google SpreadSheets'):
        self.SPREADSHEET_TITLE = title
        self.CLIENT_SECRET_FILE = client_secret_json
        self.APPLICATION_NAME = app_name

    def _get_scope(self, token_type):
        """Selecting type of scope for making request to Spreadsheet API or to Drive API

        :param token_type: <str> - expect 'drive' or 'spreadsheet' token type
        :return: <str> - url
        """
        scope = None
        if token_type == _DRIVE_TOKEN:
            scope = 'https://www.googleapis.com/auth/drive'
        elif token_type == _SPREADSHEET_TOKEN:
            scope = 'https://www.googleapis.com/auth/spreadsheets'
        return scope

    def _get_credentials(self, token_type):
        """ Getting Service account credentials from JSON file

        :param token_type: <str> - expect 'drive' or 'spreadsheet' token type
        :return: obtained credential.
        """
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.CLIENT_SECRET_FILE,
                                                                       self._get_scope(token_type))
        return credentials

    def _get_connection(self, token_type):
        """Creating a Sheets API service object

        :param token_type: <str> - expect 'drive' or 'spreadsheet' token type
        :return: <object> - Sheets API service object
        """
        credentials = self._get_credentials(token_type)
        http = credentials.authorize(httplib2.Http())
        service = None
        if token_type == _SPREADSHEET_TOKEN:
            service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=_DISCOVERY_URL)
        elif token_type == _DRIVE_TOKEN:
            service = discovery.build('drive', 'v3', http=http)
        return service

    def record_data(self, output_data, spreadsheet_id, sheet_range=None):
        """Recording data to the spreadsheet

        :param output_data: <list> - data for recording to Spreadsheet
        :param spreadsheet_id: <str> - id of modifying spreadsheet
        :param sheet_range: <str> - range of columns(Example - 'A3:B10').
        :return: <dict> - response from Google
        """
        token_type = _SPREADSHEET_TOKEN
        ascii_number = 96  # number of last non alphabet digit in ASCII table, for setting a second part of table-range
        max_column = 0
        value_input_option = "USER_ENTERED"  # according to Google Sheets API manual:
        #  "The values will be parsed as if the user typed them into the UI"

        for i in range(len(output_data)):
            if max_column < len(output_data[i]):
                max_column = len(output_data[i])
        body = {
            'values': output_data
        }
        service = self._get_connection(token_type)
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
            _logger.error('Seems, that you pass invalid data. Please, check you input data and try again')
            request = None
        return request

    def _create_spreadsheet(self):
        """Creating an empty spreadsheet

        :return: <str> - spreadsheet id
        """
        token_type = _SPREADSHEET_TOKEN

        service = self._get_connection(token_type)
        request = service.spreadsheets().create(body={"properties": {"title": self.SPREADSHEET_TITLE}}).execute()
        _logger.info('Response from Google: {}'.format(_nice_format(request)))
        _logger.info('New spreadsheet with URL {} was created'.format(
            'https://docs.google.com/spreadsheets/d/' + request.get('spreadsheetId'))
        )
        return request.get('spreadsheetId')

    def get_spreadsheet_data(self, spreadsheet_id, sheet_name, sheet_range):
        """Getting data from spreadsheet by sheet name and sheet range

        :param spreadsheet_id: <str> - id of modifying spreadsheet
        :param sheet_name: <str> - name of sheet, from which the data will be taken(e.g.: Sheet1)
        :param sheet_range: <str> - range of columns(e.g: 'A3:B10')
        :return: <list> - array of values from selected sheet in spreadsheet
        """
        token_type = _SPREADSHEET_TOKEN
        range_body = str(sheet_name) + '!' + str(sheet_range)
        service = self._get_connection(token_type)
        request = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_body
        ).execute()
        values = request.get('values')
        _logger.info('Received values: {}'.format(_nice_format(values)))
        return values

    def spreadsheet_constructor(self, output_data=None):
        """This method creates a new spreadsheet with access permission only for owner of Google API Service account.
        To specify permission, use 'add_permission' method
        If output_data not defined, spreadsheet will be empty. Otherwise, it creates a new spreadsheet
        with data from output_data(see output_data list structure below)

        :param output_data: <list> - data for recording to Spreadsheet
        example:
        output_data = [
            ['Iron Man', 'Tony Stark'],
            [43, 1.75, 80],
            ['Just like his costume;-]']
        ]
        :return: <str> - the id of created spreadsheet
        """
        spreadsheet_id = self._create_spreadsheet()
        if output_data:
            record = self.record_data(output_data, spreadsheet_id)
            _logger.info('Data was recorded. Response: {}'.format(_nice_format(record)))
        return spreadsheet_id

    def _set_permission_service(self, spreadsheet_id, token_type, permission_operation, body=None, permission_id=None):
        """ If permission_operation is adding new permission, then method send request to change permission
        for the selected spreadsheet.
        If permission_operation is showing all permission, then method send request to get all permissions
        for the selected spreadsheet.

        :param spreadsheet_id: <str> - spreadsheet id
        :param token_type: <str> - expect 'drive' or 'spreadsheet' token type
        :param permission_operation: <str> - expect 'add', 'show' or 'remove'
        :param body: <dict> - properties of request
        :param permission_id: <str> - id of permission to delete(can get in from response of show_permission-method)
        :return: <dict> - response from Google
        """
        if permission_operation == PERMISSION_OPERATION['ADD']:
            service = self._get_connection(token_type)
            request = service.permissions().create(
                fileId=spreadsheet_id,
                sendNotificationEmail=False,
                body=body
            ).execute()
            return request

        elif permission_operation == PERMISSION_OPERATION['SHOW']:
            service = self._get_connection(token_type)
            request = service.permissions().list(
                fileId=spreadsheet_id,
                fields='permissions'
            ).execute()
            return request

        elif permission_operation == PERMISSION_OPERATION['REMOVE']:
            service = self._get_connection(token_type)
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
        token_type = _DRIVE_TOKEN
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

        if permission_type != PERMISSION_TYPES['SHARE_EVERYONE'] and permission_type != PERMISSION_TYPES['DEFAULT']:
            if user_email:
                if permission_type == PERMISSION_TYPES['SET_READER']:
                    request = self._set_permission_service(
                        spreadsheet_id,
                        token_type,
                        PERMISSION_OPERATION['ADD'],
                        permissions['set_reader']
                    )
                    response = request
                elif permission_type == PERMISSION_TYPES['SET_WRITER']:
                    request = self._set_permission_service(
                        spreadsheet_id,
                        token_type,
                        PERMISSION_OPERATION['ADD'],
                        permissions['set_writer']
                    )
                    response = request
            else:
                _logger.error('User email is not defined.')
                return None
        elif permission_type == PERMISSION_TYPES['SHARE_EVERYONE']:
            request = self._set_permission_service(
                spreadsheet_id,
                token_type,
                PERMISSION_OPERATION['ADD'],
                permissions['share_everyone']
            )
            response = request
        elif permission_type == PERMISSION_TYPES['DEFAULT']:
            request = self._set_permission_service(
                spreadsheet_id,
                token_type,
                PERMISSION_OPERATION['ADD'],
                permissions['access_by_link']
            )
            response = request
        else:
            _logger.error('Input data is not valid.')
            return None
        _logger.info('Received response {}'.format(_nice_format(response)))
        return response

    def show_permissions(self, spreadsheet_id):
        """Showing all permissions of selected spreadsheet
        :param spreadsheet_id: <str> - spreadsheet id
        :return: <dict> - permissions
        """
        token_type = _DRIVE_TOKEN
        response = self._set_permission_service(spreadsheet_id, token_type, PERMISSION_OPERATION['SHOW'])
        spreadsheet_permissions = response['permissions']
        _logger.info('Received response {}'.format(_nice_format(spreadsheet_permissions)))
        return spreadsheet_permissions

    def remove_permission(self, spreadsheet_id, permission_id):
        """Removing permission of selected spreadsheet

        :param spreadsheet_id: <str> - spreadsheet id
        :param permission_id: <str> - id of permission to delete(can get in from response of show_permission-method)
        :return: response form API
        """
        token_type = _DRIVE_TOKEN
        response = self._set_permission_service(spreadsheet_id, token_type, PERMISSION_OPERATION['REMOVE'],
                                                permission_id=permission_id)
        _logger.info('Received response {}'.format(_nice_format(response)))
        return response

