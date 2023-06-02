import asyncio
import json
import os
import sys
import time
import random
import secrets
import string
import concurrent.futures


from selenium_stealth import stealth
import undetected_chromedriver as webdriver
from utils.CustomChrome import ProxyExtension
from utils.Proxy import Proxy
from selenium.webdriver.common.by import By
from api import ApiSiteSM
from utils.get_product_values import get_product_values
from utils.Excel import Excel
from utils.IOTxt import IOTxt
from utils.UserAgents import UserAgents

excel = Excel(r'C:\Users\kiril\Desktop\SM\Auto_Cart\Cookie\Befor_Check.xlsx',
              r'C:\Users\kiril\Desktop\SM\Auto_Cart\Cookie\After_Check.xlsx')
txt = IOTxt(r'C:\Users\kiril\Desktop\SM\Auto_Cart\Cookie\items.txt')
user_agent = UserAgents()


async def main():
    cookie_excel = []
    is_point_successful = False

    try:
        is_count = excel.check_rows_exist()
        if not is_count:
            raise ValueError("The rows in the table have ended")

        proxy_obj = Proxy()

        proxy_url = proxy_obj.proxy
        proxy = proxy_obj.proxy_ProxyExtension

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

        cookie_excel = excel.get_excel()

        driver.get("https://www.sportmaster.ru/")
        # driver.get("https://2ip.ru/")

        cookies = json.loads(cookie_excel[2])
        for cookie in cookies:
            driver.add_cookie(cookie)

        await asyncio.sleep(5)
        dump_cookie = driver.get_cookies()
        cookies = {cookie['name']: cookie['value'] for cookie in dump_cookie}

        api_requests = ApiSiteSM(ua, cookies, proxy_url)

        status_code, response_body = await api_requests.profile_info()
        if "phone" not in response_body:
            raise ValueError("Error: auth")

        product_id = None
        while True:
            for i in range(3):
                status_code, response_body = await api_requests.catalog_api()
                if status_code != 200:
                    raise ValueError("Error: catalog_api")

                product_id, product_ware_id = get_product_values(response_body)
                if not product_id:
                    print("прошел круг catalog_api")
                    continue
                else:
                    break
            if not product_id:
                print(response_body)
                raise ValueError("Error: product_id - get_product_values")

            if txt.check_product_number(product_id):
                continue

            status_code, response_body = await api_requests.product_view(product_id)

            if status_code != 200:
                raise ValueError("Error: product_view")

            marks = response_body.get("marks")
            if "BONUSNA" not in marks:
                break

        driver.get(f'https://www.sportmaster.ru/product/{product_id}/')
        await asyncio.sleep(5)

        buttons = driver.find_elements(By.CSS_SELECTOR, '[data-selenium="product-sizes-item"]')

        while True:
            # Фильтрация кнопок, удаляя кнопки с классом "sm-product-size__button--disabled"
            filtered_buttons = [button for button in buttons if
                                "sm-product-size__button--disabled" not in button.get_attribute("class")]

            # Проверка наличия кнопок
            if not filtered_buttons:
                # Если нет доступных кнопок, прерываем цикл
                break

            # Выбор случайной кнопки из отфильтрованного списка
            random_button = random.choice(filtered_buttons)

            random_button.click()
            await asyncio.sleep(2)

            try:
                element = driver.find_element(By.CSS_SELECTOR, 'a.sm-product-pickup__link.sm-link.sm-link_darkblue')
                text = element.text
                count_available_shop = int(''.join(filter(str.isdigit, text)))

                if count_available_shop >= 1:
                    # Если есть хотя бы один доступный магазин, добавляем в корзину
                    button = driver.find_element(By.CSS_SELECTOR, '[data-test-id="add-to-cart-btn"]')
                    button.click()
                    await asyncio.sleep(2)
                    txt.append_product_number(product_id)
                    break
                else:
                    # Если нет доступных магазинов, удаляем выбранную кнопку из списка и повторяем цикл
                    buttons.remove(random_button)
            except:
                continue

        is_point_successful = True

        try:
            button = driver.find_element(By.CSS_SELECTOR,
                                         '.sm-button.sm-buy-button-new__go-to-cart[data-selenium="smButton"][href="/cart/"]')
            button.click()
            await asyncio.sleep(2)
        except:
            button = driver.find_element(By.CSS_SELECTOR,
                                         '.sm-button.sm-product-recommendations-dialog__action-button.sm-button--blue.sm-button--s[data-selenium="smButton"][href="/cart/"]')
            button.click()
            await asyncio.sleep(2)

        elements = driver.find_elements(By.CSS_SELECTOR, '[data-selenium="cartTitle"]')

        if len(elements) == 0:
            driver.get('https://www.sportmaster.ru/cart/')
            # print("перешел по cart")
            await asyncio.sleep(5)

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

        try:
            button = driver.find_element(By.CSS_SELECTOR, '.payment-method.sm-payment-type[data-selenium="IN_STORE"]')
            button.click()
            await asyncio.sleep(2)
        except:
            pass
        # print("успех")


    finally:
        if is_point_successful is True:
            excel.finally_add(cookie_excel)
        else:
            excel.finally_add(cookie_excel, "IN")
        await asyncio.sleep(2)
        if 'driver' in locals():
            driver.close()
            driver.quit()
            del driver


def generate_hash(length):
    characters = string.ascii_letters + string.digits
    hash = ''.join(secrets.choice(characters) for _ in range(length))
    return hash


def run_in_thread(loop):
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except Exception as e:
        print("Error in thread: ", e)


if __name__ == "__main__":
    # arrays_in = sys.argv
    # serialized_data = arrays_in[1]
    # config = json.loads(serialized_data)

    # try:
    #     button = 1
    #     button.click()
    # except Exception as e:
    #     # raise "Вызвал ошибку"
    #     traceback.print_exc()

    for i in range(1):
        try:
            # asyncio.run(main())
            loop1 = asyncio.new_event_loop()
            # loop2 = asyncio.new_event_loop()
            # loop3 = asyncio.new_event_loop()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(run_in_thread, loop1)
                # executor.submit(run_in_thread, loop2)
                # executor.submit(run_in_thread, loop3)

            result = {
                "result": True
            }
            json_data = json.dumps(result)
            # sys.stdout.flush()
            print(json_data)
        except Exception as e:
            hash = generate_hash(10)
            print(e)
            # directory = 'error_files'
            # filepath = os.path.join(directory, f"{hash}.txt")
            # with open(filepath, "a") as file:
            #     file.write(str(e))
            #
            # result = {
            #     "result": False,
            #     "number": hash
            # }
            # json_data = json.dumps(result)
            # sys.stdout.flush()
            # print(json_data)
