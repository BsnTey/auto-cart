import asyncio
import json
import os
import sys
import time
import random
import secrets
import string
import concurrent.futures
import multiprocessing
import traceback

from selenium.common import ElementClickInterceptedException
from selenium_stealth import stealth
import undetected_chromedriver as webdriver
from utils.CustomChrome import ProxyExtension
from utils.Proxy import Proxy
from selenium.webdriver.common.by import By
from api import ApiSiteSM
from utils.get_product_values import get_product_values
from utils.find_product import find_product_catalog, find_product_view
from utils.IOTxt import IOTxt
from utils.UserAgents import UserAgents

txt = IOTxt(r'C:\Users\kiril\Desktop\SM\Auto_Cart\Cookie\items.txt')
# excel = Excel(r'C:\Users\kiril\Desktop\SM\Auto_Cart\Cookie\Befor_Check.xlsx',
#               r'C:\Users\kiril\Desktop\SM\Auto_Cart\Cookie\After_Check.xlsx')

user_agent = UserAgents()
is_point_successful = False


async def main(proxy, cookie):
    global is_point_successful
    try:

        proxy_obj = Proxy(proxy)
        proxy_url = proxy_obj.proxy
        proxy = proxy_obj.proxy_ProxyExtension

        for i in range(2):
            try:

                proxy_extension = ProxyExtension(*proxy)
                ua = user_agent.choice()
                options = webdriver.ChromeOptions()
                options.add_argument(f"--load-extension={proxy_extension.directory}")
                driver = webdriver.Chrome(options=options)

                # driver.set_page_load_timeout(10)
                stealth(driver,
                        user_agent=ua,
                        languages=["ru-RU", "ru"],
                        vendor="Google Inc.",
                        platform="Wind32",
                        webgl_vendor="Intel Inc.",
                        renderer="Intel Iris OpenGL Engine",
                        fix_hairline=True
                        )

                # cookie_excel = excel.get_excel()

                driver.get("https://www.sportmaster.ru/")
                # driver.get("https://2ip.ru/")
                break
            except:
                if 'driver' in locals():
                    driver.close()
                    driver.quit()
                    del driver

        cookies = json.loads(cookie)
        for cookie in cookies:
            driver.add_cookie(cookie)

        await asyncio.sleep(5)
        driver.set_window_position(-300, 0)
        dump_cookie = driver.get_cookies()
        cookies = {cookie['name']: cookie['value'] for cookie in dump_cookie}

        api_requests = ApiSiteSM(ua, cookies, proxy_url)

        status_code, response_body = await api_requests.profile_info()
        if "phone" not in response_body:
            raise ValueError("Error: auth")

        while True:
            for i in range(10):
                product_id, product_ware_id = await find_product_catalog(api_requests)
                if not product_id:
                    continue

                if txt.check_product_number(product_id):
                    continue

                is_valid_product_id = await find_product_view(api_requests, product_id)
                if is_valid_product_id:
                    break

            if not product_id:
                raise ValueError("Error: product_id")

            driver.get(f'https://www.sportmaster.ru/product/{product_id}/')
            await asyncio.sleep(5)

            driver.execute_script("window.scrollBy(0, 200);")
            buttons = driver.find_elements(By.CSS_SELECTOR, '[data-selenium="product-sizes-item"]')
            # Фильтрация кнопок, удаляя кнопки с классом "sm-product-size__button--disabled"
            filtered_buttons = [button for button in buttons if
                                "sm-product-size__button--disabled" not in button.get_attribute("class")]

            # Проверка наличия кнопок
            if not filtered_buttons:
                # Если нет доступных кнопок, прерываем цикл
                continue

            # Выбор случайной кнопки из отфильтрованного списка
            random_button = random.choice(filtered_buttons)

            random_button.click()

            await asyncio.sleep(2)
            driver.set_window_position(-500, 0)
            try:
                element = driver.find_element(By.CSS_SELECTOR, 'a.sm-product-pickup__link.sm-link.sm-link_darkblue')
                text = element.text
                count_available_shop = int(''.join(filter(str.isdigit, text)))

                if count_available_shop >= 1:
                    # Если есть хотя бы один доступный магазин, добавляем в корзину
                    button = driver.find_element(By.CSS_SELECTOR, '[data-test-id="add-to-cart-btn"]')
                    button.click()
                    await asyncio.sleep(2)
                    is_point_successful = True

                    txt.append_product_number(product_id)
                    break
                else:
                    # Если нет доступных магазинов, удаляем выбранную кнопку из списка и повторяем цикл
                    buttons.remove(random_button)
            except:
                continue

        try:
            button = driver.find_element(By.CSS_SELECTOR,
                                         '.sm-button.sm-buy-button-new__go-to-cart[data-selenium="smButton"][href="/cart/"]')
            button.click()
            await asyncio.sleep(2)
        except ElementClickInterceptedException:
            button = driver.find_element(By.CSS_SELECTOR,
                                         '.sm-button.sm-product-recommendations-dialog__action-button.sm-button--blue.sm-button--s[data-selenium="smButton"][href="/cart/"]')
            button.click()
            await asyncio.sleep(2)
        except Exception as e:
            elements = driver.find_elements(By.CSS_SELECTOR, '[data-selenium="cartTitle"]')
            if len(elements) == 0:
                driver.get('https://www.sportmaster.ru/cart/')
                await asyncio.sleep(5)

        try:
            elements = driver.find_elements(By.CSS_SELECTOR, '[data-selenium="cartTitle"]')
            if len(elements) == 0:
                driver.get('https://www.sportmaster.ru/cart/')
                await asyncio.sleep(5)
            driver.set_window_position(-600, 0)
            button = driver.find_element(By.CSS_SELECTOR, '[data-selenium="pickup"]')

            button.click()
            await asyncio.sleep(5)

            xpath_expression = '//*[@data-selenium="pickup-point" and contains(@id, "SHOP")]'

            button = driver.find_element(By.XPATH, xpath_expression)

            button.click()
            await asyncio.sleep(2)

            button = driver.find_element(By.CSS_SELECTOR, '[data-selenium="select-btn"]')

            button.click()
            await asyncio.sleep(2)

            button = driver.find_element(By.CSS_SELECTOR, '.payment-method.sm-payment-type[data-selenium="IN_STORE"]')
            button.click()
            await asyncio.sleep(2)
        except:
            pass

    except Exception as e:
        raise e

    finally:
        await asyncio.sleep(2)
        if 'driver' in locals():
            driver.close()
            driver.quit()
            del driver


async def async_main(proxy, cookie):
    await main(proxy, cookie)


def generate_hash(length):
    characters = string.ascii_letters + string.digits
    hash = ''.join(secrets.choice(characters) for _ in range(length))
    return hash


if __name__ == "__main__":
    arrays_in = sys.argv
    proxy = arrays_in[1].strip()
    cookie = arrays_in[2].strip()

    # proxy = "socks5://MEwluo:Ljeic0GMlo@188.130.221.118:5501"
    # cookie = '[{"domain": "www.sportmaster.ru","name": "SMID","path": "/","value": "eyJhbGciOiJSUzI1NiJ9.eyJqdGkiOiIzMjU4MzgwMS01NmY2LTRiZTgtYWQ2Yy0xOGU2NDZlYjRiYmMiLCJpc3MiOiJTTTMwIiwiaWF0IjoxNjg2MDY5MjAxLCJhdWQiOiJzcG9ydG1hc3RlciIsImFuVCI6IjJiZmM1MWIwLWViNzgtNDEzMi1iZDEyLTg0NmQyNGMxZTJhNiIsImFuUCI6IjUxZjczMmUwLTY0N2ItNDY2OC05NDU2LTJjZWQwMjA4ZjAyOSIsImFuVSI6IjEwMDAwMDAwNjM4OTAzMTQzOCIsImNhblAiOiJBSUNNcmZNL3Q1ZVlzbWl3N1k0NDlidjRtRVprRkp4K2FaVWFXMFdRTDFacGJ5OTZwalQzblYrNFA3R0cxLzVrQzliZEx1ZkwwQkNWTVlLVTduL1BsYVh4NzQ3Z0syVXlMNysyTHJvS1FvdjEwM29OaE5qd2RMVS9mL1ZjTGxYRzFqMTZWWjBXcVV6a0JoOGszUlJaUEF5RWVIYzdvUnhnUGdLcTF1MnlNbEs1YllzU1lCUnllckhDalRXSFliSXA1endxU1N1SHNvQ1haVzRFWEY5YjBJdU9MOHlyMDZjU1BmSUcxYWR6ZEJ3eUhqK3lOQis1ZGpudEpWMXZJZXM0bTFzPSIsImNhblQiOiJBSUFnQlhDL3ovUVVnVzRsQXE0Qko5bkJxR2dqNnJVRkc1RmFkdDBBdEg3YnJVQjA1dkVNSFptaEpVYTZFWW5aYjRGUVJoVEdvaVlnZnh3cEoweHNRaHBUMWJkalNnaEFoT05HdmhEMWZRMXVyUHIrUUhXcWZpcG5RWVlOYlp5MjZuK25aamh5eFdiSHRFUVhMNFFnZlhCRjBEK1hHMmphamtyL05FYVlrdDhFcnQzNXkzNlpHZGh3ckxpb25EcURmanFlZ1I1VFRBU3RqSndkRDBwbVRMRHh0dUVQanZlczFVOWhCMmd1Vzc4R3YxcUpDaTFCS0Z2RncwK1kwSTE0UFVrPSIsImF1VCI6ImNmZDIyNmNkLTQwNDgtNGNhYS1iZWU1LWQ2ZGM5YzA3OWNmZCIsImF1UCI6IjEwMDAwMDAwNjM4OTAzMDU2MCIsImNhdVQiOiJBSUFQM1dGbGJBK25paG9IWi94VDBNcE01bzdUZ05TbVd0cGNsN3p3bmJJL1N6c0s2NERtOHJsaDBiSFF6eGRkbk5mYXE2cjBPQlB1T0VNRFhZNE9FWEh6dnlCRkgrNjVNNHhyWDhVS0dLSk95MHdwRFgyVndNbVRGMnY4ZGkrdkIvTkdQQWx5ZE85NmhpbjBIL1Jqd0FaMlpmT1lwRzVkNnNwTEViTEwrOGpWa1FFS1UyVy9RaVVvWVIwNzh2VVFtVGdGQVdScFg4UmVTdFpkcFhGMndGaVl6cW4vbFhCekkzWVVNWEQ4ekJseVAyRk1GV1ZRZXk4TUgvbGthRkxMc0JZPSIsInYiOiJWMiJ9.OncHOXSK5sVk0BJvgk1hQZ1HQFsFr540NHLb6W4K924Z0aEWcGaRZoWj7-IjtSme40odGLbRi9m1tnbuv8ujARkLBk79z4Qg8UNZy_dXESq_wC4kKNxbnoIC4NP_3VMJFPSFiXhuYJbOWM1VgQMGAqlK6Qq_AE9ZBfiiZBUJIq2C9yhkQ8y9l0ZD0JbHt-tIPYJRZIHXR0xi3HFqhcdYjntXqkyIJoNlrGHTVSWfmkVoska1ogPCSyOH4c8maWpb4hxdff9AYaBI-ULMd0vSvTkYHIy1DjC4pQPil6X5JNrwl3g6_5Wz11oo5THR89sKP_kVmK5hswERVsiHc-YPRA"}]'
    try:
        asyncio.run(async_main(proxy, cookie))
    except Exception as e:
        hash = generate_hash(10)
        print(e)
    finally:
        print(is_point_successful)
