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