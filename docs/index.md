<p>To create Google Spreadsheet using PythonGoogleSpreadsheet first of all, you need Service account key for 
    access to Google API. Using following instruction, create a new project in 
    <a href="https://console.developers.google.com/cloud-resource-manager">Google Dewelopers console</a> and get it:
</p>
<ol>
    <li>Open up <a href="https://console.developers.google.com/cloud-resource-manager">Google Dewelopers console</a>. 
        You'll see the list of your projects. Press "CREATE PROJECT" and using tips create the new one.
        <img src="https://raw.githubusercontent.com/HolmesInc/PythonGoogleSpreadsheet/master/docs/1_dev_console.jpg">
    </li>
    <li>When you'll receive message, that the project started, open up 
        <a href="https://console.developers.google.com/apis/library?project=pages-test">"APIs & services"</a>. Here 
        You need to activate Drive API and Sheets API. 
        <img src="https://raw.githubusercontent.com/HolmesInc/PythonGoogleSpreadsheet/master/docs/2_activating_apis.jpg">
    </li>
    <li>Then click on 'hamburger' to open menu and select "IAM & admin" -> "Service accounts" 
        <img src="https://raw.githubusercontent.com/HolmesInc/PythonGoogleSpreadsheet/master/docs/3_service_account.jpg">
        On this page click "CREATE SERVICE ACCOUNT". Enter Service account name, select a Role (this field you can 
        live without any changes), enable "Furnish a new private key", select Key type JSON and click "CREATE".
        <img src="https://raw.githubusercontent.com/HolmesInc/PythonGoogleSpreadsheet/master/docs/4_creating_serv_acc.jpg">
    </li>
    <li>Change name of downloaded JSON file to client_secret.json and put it to the root of your project.
    </li>
</ol>
<p>PythonGoogleSpreadsheet methods, which you can use:</p>
<ol>
    <li>
        <pre>spreadsheet_constructor(output_data=None)</pre>
        This method creates a new spreadsheet with access permission only for owner of Google API Service account.
        To specify permission, use 'add_permission' method. If output_data not defined, spreadsheet will be empty. 
        Otherwise, it creates a new spreadsheet with data from output_data (look at the 
        <a href="https://github.com/HolmesInc/PythonGoogleSpreadsheet/tree/master/examples">examples</a>)
    </li>
    <li>
        <pre>record_data(output_data, spreadsheet_id, sheet_range=None)</pre>
        Recording data to the spreadsheet. If sheet_range was specified, data records according to specified range. 
        Otherwise recording starts from A1:A1
    </li>
    <li>
        <pre>get_spreadsheet_data(spreadsheet_id, sheet_name, sheet_range)</pre>
        Getting data from selected spreadsheet(spreadsheet_id) by sheet name(e.g.: Sheet1) and sheet range(e.g: 'A3:B10')
        REMARK: sheet_name have to contain only letters of Latin alphabet
    </li>
    <li>
        <pre>add_permission(spreadsheet_id, permission_type, user_email=None)</pre>
        Adding new permission to spreadsheet(spreadsheet_id). Select Permission type from dictionary PERMISSION_TYPES,
        which you can import from PythonGoogleSpreadsheet. If you'll select SET_WRITER or SET_READER, you have to pass 
        user_email to this method.
    </li>
    <li>
        <pre>show_permissions(spreadsheet_id)</pre>
        Showing all permissions of selected spreadsheet
    </li>
    <li>
        <pre>remove_permission(spreadsheet_id, permission_id)</pre>
        Removing permission of selected spreadsheet
    </li>
</ol>


