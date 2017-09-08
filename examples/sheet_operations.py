import os
from PythonGoogleSpreadsheet.PythonGoogleSpreadsheet import SpreadsheetWorker, PERMISSION_TYPES


def create_spreadsheet():
	_g_spreadsheet_client = os.path.abspath('client_secret.json')
	spreadsheet_worker = SpreadsheetWorker(_g_spreadsheet_client, app_name='Sheets Test')
	spreadsheet_worker.SPREADSHEET_TITLE = "You test spreadsheet"
	output_data = [
            ['Iron Man', 'Tony Stark'],
            [43, 1.75, 80],
            ['Just like his costume;-]']
        ]
	spreadsheet_id = spreadsheet_worker.spreadsheet_constructor(output_data)
	spreadsheet_worker.add_permission(spreadsheet_id, PERMISSION_TYPES['DEFAULT'])
	spreadsheet_data = spreadsheet_worker.get_spreadsheet_data(spreadsheet_id, 'Sheet1', 'A3:B10')
	print(spreadsheet_id)
	print(spreadsheet_data)



if __name__ == '__main__':
	create_spreadsheet()