from fake_useragent import UserAgent

class Headers:
    def __init__(self, user_agent):
        self.user_agent = user_agent


    def get_general_headers(self):
        return {
            'User-Agent': self.user_agent,
            "Host": "www.sportmaster.ru",
            "Connection": "keep-alive",
            "sec-ch-ua": 'Not A;Brand";v="99", "Chromium";v="99", "Microsoft Edge";v="99',
            "Accept": "application/json, text/plain, */*",
            "X-SM-Accept-Language": "ru-RU",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
            "referer": "https://www.sportmaster.ru/"
        }

    def get_product_view_headers(self, product_id):
        return {
            'User-Agent': self.user_agent,
            "Host": "www.sportmaster.ru",
            "Connection": "keep-alive",
            "sec-ch-ua": 'Not A;Brand";v="99", "Chromium";v="99", "Microsoft Edge";v="99',
            "Accept": "application/json, text/plain, */*",
            "X-SM-Accept-Language": "ru-RU",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
            "referer": f"https://www.sportmaster.ru/product/{product_id}/"
        }
