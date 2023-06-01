import httpx
from httpx_socks import AsyncProxyTransport
from headers import Headers
import random
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



class ApiSiteSM:
    def __init__(self, cookies, proxies):
        self.headers_obj = Headers()
        self.cookies = cookies
        self.headers = self.headers_obj.get_general_headers()

        # прокси для socks5. Пример "socks5://MEwluo:Ljeic0GMlo@46.8.22.214:5501" (порт socks5)
        # self.client = httpx.AsyncClient(transport=AsyncProxyTransport.from_url(proxies))

        # прокси для http. Пример "http://MEwluo:Ljeic0GMlo@46.8.22.214:5500" (порт http)
        self.client = httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(proxy=httpx.Proxy(proxies)))


    async def catalog_api(self):
        catalog_link = ["zhenskaya_odezhda/vetrovki",
                        "zhenskaya_obuv/krossovki",
                        "muzhskaya_odezhda/vetrovki",
                        "muzhskaya_obuv/krossovki",
                        "muzhskaya_obuv/polubotinki"]

        random_link = random.choice(catalog_link)
        random_page = random.randint(1, 5)

        body = {
            "url": f"/catalog/{random_link}/?page={random_page}",
            "page": random_page + 1
        }

        response = await self.client.post('https://www.sportmaster.ru/web-api/v1/catalog/', headers=self.headers,
                                          cookies=self.cookies, json=body)
        status_code = response.status_code
        response_body = response.json()

        return status_code, response_body

    async def product_view(self, product_id):
        headers = self.headers_obj.get_product_view_headers(product_id)
        response = await self.client.get(f'https://www.sportmaster.ru/ga-api/v1/product-view/{product_id}',
                                         headers=headers, cookies=self.cookies)

        status_code = response.status_code
        response_body = response.json()

        return status_code, response_body

    async def profile_info(self):
        response = await self.client.get('https://www.sportmaster.ru/web-api/v1/profile/info/', headers=self.headers,
                                         cookies=self.cookies)

        status_code = response.status_code
        if status_code == 200:
            response_body = response.json()
            return status_code, response_body
        return status_code, "error"
