import datetime
import gspread as gc
import os
from oauth2client.service_account import ServiceAccountCredentials

from enums import month_name


class SpreadsheetsWorker:
    def __init__(self):
        credentials = os.getenv('CREDENTIALS_FILE', '../config/creds.json')
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
        #self.first_day_outlay_cell = os.getenv('FIRST_DAY_OUTLAY_CELL', 'G3')
        #self.last_day_outlay_cell = os.getenv('LAST_DAY_OUTLAY_CELL', 'AK11')
        #self.days_cell_range = f"{self.first_day_outlay_cell}:{self.last_day_outlay_cell}"
        self.days_cell_range = os.getenv('OUTLAY_CELL', 'G3:AK11')

        self.current_worksheet = self.__auto_set_current_worksheet()
        self.current_day = self.__auto_set_current_day()

        self.category_cells = os.getenv('CATEGORY_CELLS', 'B3:D12')
        self.category_dict = self.__get_category_list()

    def new_values_for_day(self, category, value):
        row = self.category_dict[category]
        column = self.current_day.col
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

    def __get_category_list(self):
        cell_list = self.current_worksheet.range(self.category_cells)
        category_dict = {x.value: x.row for x in cell_list if x.value}
        return category_dict

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


a = SpreadsheetsWorker()
a.new_values_for_day('Продукты', 100)
#a.update_cell('A0', 'Jopa')