import os
from PythonGoogleSpreadsheet import SpreadsheetWorker, PERMISSION_TYPES


def create_spreadsheet():
    _g_spreadsheet_client = os.path.abspath('client_secret.json')
    spreadsheet_worker = SpreadsheetWorker(_g_spreadsheet_client, app_name='Sheets Test')
    spreadsheet_worker.SPREADSHEET_TITLE = "You test spreadsheet"
    output_data = [
        ['Iron Man', 'Tony Stark'],
        [43, 1.75, 80],
        ['Just like his costume;-]']
    ]
    spreadsheet_object = spreadsheet_worker.spreadsheet_constructor(output_data)
    spreadsheet_worker.add_permission(spreadsheet_object.spreadsheet_id, PERMISSION_TYPES['DEFAULT'])
    spreadsheet_data = spreadsheet_worker.get_spreadsheet_data(spreadsheet_object.spreadsheet_id, 'Sheet1', 'A1:C3')
    print('Spreadsheet ID: ', spreadsheet_object.spreadsheet_id)
    print('Spreadsheet URL: ', spreadsheet_object.spreadsheet_url)
    print('Spreadsheet Data: ', spreadsheet_data)


if __name__ == '__main__':
    create_spreadsheet()
