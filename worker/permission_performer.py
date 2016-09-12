import httplib2
from apiclient import discovery
import oauth2client
from oauth2client import client, tools

import os
import logging as _logger

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/google-drive-token.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Creating Google Sheets'


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
    credential_path = os.path.join(credential_dir,
                                   'google-drive-token.json')

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

def modify_permissions():
    """Modify file permissions

    :param spreadsheet_id <string> - id of spreadsheet to modify they access permission

    :return <dict>
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    results = service.permissions().create(fileId="1n8xzIVZqDJFjKig_BYk09RgaIl2H21jBxycVYip9VUQ", sendNotificationEmail=False, body={"type": "anyone", "role": "reader"}).execute()

    print(results)
    _logger.warning(results)
   

if __name__ == '__main__':
    modify_permissions()