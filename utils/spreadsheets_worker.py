import datetime
import gspread as gc
import os
from oauth2client.service_account import ServiceAccountCredentials

from enums import month_name


class SpreadsheetsWorker:
    def __init__(self):
        credentials = os.getenv('CREDENTIALS_FILE', './config/creds.json')
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials, scope)
        self.gc = gc.authorize(credentials)
        self.sheets_name = os.getenv('SHEETS_NAME', 'WalletSheets-2019')
        try:
            sh = self.gc.open(self.sheets_name)
        except gc.SpreadsheetNotFound:
            sh = self.gc.create(self.sheets_name)
            sh.share(os.getenv('MY_EMAIL', 'NicknameSoHard@gmail.com'),
                     perm_type='user',
                     role='writer')
        self.sheets = sh
        self.worksheets = self.sheets.worksheets()

        self.month_names = month_name.month_names
        self.days_cell_range = os.getenv('OUTLAY_CELL', 'G3:AK11')

        self.current_worksheet = self.__auto_set_current_worksheet()
        self.current_day = self.__auto_set_current_day()

        self.outlay_category_cells = os.getenv('CATEGORY_OUTLAY_CELLS', 'B3:D12')
        self.outlay_category_dict = self.__get_category_list(self.outlay_category_cells)

        self.income_category_cells = os.getenv('CATEGORY_INCOME_CELLS', 'B21:D24')
        self.income_category_dict = self.__get_category_list(self.income_category_cells)

        self.income_cell_range = os.getenv('INCOME_CELLS', 'E21:E24')
        self.income_column = self.current_worksheet.acell(self.income_cell_range.split(':')[0]).col

    def get_category_list(self, category_type='outlay'):
        if category_type == 'outlay':
            return list(self.outlay_category_dict.keys())
        elif category_type == 'income':
            return list(self.income_category_dict.keys())
        else:
            return None

    def new_value_for_day(self, category_type, category, value):
        if category_type == 'outlay':
            row = self.outlay_category_dict[category]
            column = self.current_day.col
        else:
            row = self.income_category_dict[category]
            column = self.income_column
        current_values = self.current_worksheet.cell(row=row, col=column).value
        if current_values:
            value += int(current_values)
        success = self.__update_cell((row, column), value)
        return success

    def get_worksheets(self, id_worksheets):
        try:
            if isinstance(id_worksheets, int):
                return self.sheets.get_worksheet(id_worksheets)
            elif isinstance(id_worksheets, str):
                return self.sheets.worksheet(id_worksheets)
        except gc.WorksheetNotFound:
            return None

    def __update_cell(self, coords, value):
        try:
            if isinstance(coords, str):
                self.current_worksheet.update_acell(coords, value)
            else:
                self.current_worksheet.update_cell(*coords, value)
            return True
        except gc.IncorrectCellLabel:
            return False

    def __get_category_list(self, category_cells):
        cell_list = self.current_worksheet.range(category_cells)
        outlay_category_dict = {x.value: x.row for x in cell_list if x.value}
        return outlay_category_dict

    def __auto_set_current_day(self):
        today = str(datetime.datetime.today().day)
        cell = self.current_worksheet.find(today)
        return cell

    def __auto_set_current_worksheet(self):
        month = self.month_names[datetime.datetime.today().month]
        current_worksheet = self.get_worksheets(month)
        if current_worksheet is None:
            current_worksheet = self.__add_new_wallet_worksheet(title=month)
        return current_worksheet

    def __add_new_wallet_worksheet(self, title):
        self.worksheets[-1].duplicate(new_sheet_name=title)
        worksheet = self.get_worksheets(title)

        cell_list = worksheet.range(self.days_cell_range)
        for cell in cell_list:
            cell.value = ''
        worksheet.update_cells(cell_list)
        return worksheet
