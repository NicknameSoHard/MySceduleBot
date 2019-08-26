import gspread as gc
import os
from oauth2client.service_account import ServiceAccountCredentials


class SpreadsheetsWorker:
    def __init__(self):
        credentials = os.getenv('CREDENTIALS_FILE', '../config/creds.json')
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials, scope)
        self.gc = gc.authorize(credentials)
        self.sheets_name = os.getenv('SHEETS_NAME', 'WorkSheets')
        try:
            sh = self.gc.open(self.sheets_name)
        except gc.SpreadsheetNotFound:
            sh = self.gc.create(self.sheets_name)
            sh.share(os.getenv('MY_EMAIL', 'NicknameSoHard@gmail.com'),
                     perm_type='user',
                     role='writer')
        self.sheets = sh
        self.worksheets = self.sheets.worksheets()

    def get_worksheets(self, id_worksheets):
        if isinstance(id_worksheets, int):
            return self.sheets.get_worksheet(id_worksheets)
        elif isinstance(id_worksheets, str):
            return self.sheets.worksheet("January")
        else:
            return None

    def add_worksheet(self, title, rows="20", cols="20"):
        return self.sheets.add_worksheet(title=title, rows=rows, cols=cols)
