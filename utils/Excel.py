import openpyxl
import json


class Excel:
    def __init__(self, path_in, path_out):
        self.path_in = path_in
        self.path_out = path_out

        self.email = None
        self.password_imap = None
        self.password = None
        self.cookie = None
        self.access_token = None
        self.refresh_token = None
        self.x_user = None
        self.device_id = None
        self.install_id = None

    def check_rows_exist(self):
        workbook = openpyxl.load_workbook(self.path_in)
        sheet = workbook.active

        rows = list(sheet.iter_rows())


        if len(rows) == 0:
            workbook.close()
            return False

        row_c1 = rows[0][2].value
        row_c2 = rows[0][3].value

        if (row_c1 is None or row_c1 == 'null') or \
                (row_c2 is None or row_c2 == 'null'):
            print("3")
            workbook.close()
            print("4")
            return False

        workbook.close()
        return True

    def get_excel(self):
        workbook = openpyxl.load_workbook(self.path_in)

        sheet = workbook.active

        row_number = 1
        row_values = []
        for cell in sheet[1]:
            row_values.append(cell.value)

        sheet.delete_rows(row_number)
        workbook.save(self.path_in)

        if "[" in row_values[2]:
            (
                self.email,
                self.password_imap,
                self.cookie,
                self.access_token,
                self.refresh_token,
                self.x_user,
                self.device_id,
                self.install_id
            ) = row_values
        else:
            (
                self.email,
                self.password_imap,
                self.password,
                self.cookie,
                self.access_token,
                self.refresh_token,
                self.x_user,
                self.device_id,
                self.install_id
            ) = row_values

        cookie = json.loads(self.cookie)

        workbook.close()
        return cookie

    def finally_add(self, path="OUT"):
        if self.cookie:
            if path == "OUT":
                path_out_save = self.path_out
            else:
                path_out_save = self.path_in

            workbook = openpyxl.load_workbook(path_out_save)
            sheet = workbook.active

            row = [
                self.email,
                self.password_imap,
                json.dumps(self.cookie, ensure_ascii=False).replace("\\", "").strip('"'),
                self.access_token,
                self.refresh_token,
                self.x_user,
                self.device_id,
                self.install_id
            ]

            sheet.append(row)
            workbook.save(path_out_save)
            workbook.close()
