import datetime
from threading import Lock


class IOTxt:
    lock = Lock()
    def __init__(self, file_path):
        self.file_path = file_path
        self.current_date = datetime.datetime.now().strftime("%d.%m.%Y")

    def append_product_number(self, product_number):
        with self.lock:
            with open(self.file_path, "a") as file:
                file.write(f"{product_number} {self.current_date}\n")

    def check_product_number(self, product_number):
        with self.lock:
            with open(self.file_path, "r") as file:
                lines = file.readlines()
        for line in lines:
            line = line.strip()  # Удаление символа переноса строки
            parts = line.split(" ")
            if len(parts) == 2:
                stored_product_number, stored_date = parts
                if stored_product_number == str(product_number):
                    if stored_date == self.current_date:
                        return True

        return False