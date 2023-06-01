import random
import re


class Proxy:
    def __init__(self):
        with open(r'C:\Users\kiril\Desktop\REG\Checker\proxy.txt', 'r') as f:
            proxies = f.readlines()
        proxy = random.choice(proxies).strip()

        matches = re.match(r'socks5://(\w+):(\w+)@([\d.]+):(\d+)', proxy)
        if matches:
            PROXY_USER = matches.group(1)
            PROXY_PASS = matches.group(2)
            PROXY_HOST = matches.group(3)
            PROXY_PORT = int(matches.group(4))

        self.proxy = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:5500"
        self.proxy_ProxyExtension = (PROXY_HOST, 5500, PROXY_USER, PROXY_PASS)



    # def get_proxy_split(self):
    #     matches = re.match(r'socks5://(\w+):(\w+)@([\d.]+):(\d+)', self.proxy)
    #     if matches:
    #         PROXY_USER = matches.group(1)
    #         PROXY_PASS = matches.group(2)
    #         PROXY_HOST = matches.group(3)
    #         PROXY_PORT = int(matches.group(4))
    #
    #         return (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

