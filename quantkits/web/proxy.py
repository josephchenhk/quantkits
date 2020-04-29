import requests
from quantkits import time
from bs4 import BeautifulSoup
from selenium import webdriver

def fetch_spys_proxies():
    url = "http://spys.one/en/https-ssl-proxy/"
    driver = webdriver.Chrome(executable_path='webdriver/chromedriver')
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "lxml")
    time.sleep(2)
    driver.quit()
    spydata = soup.find_all("tr", {"class": "spy1x"}) + soup.find_all("tr", {"class": "spy1xx"})
    spydata = [data.find("td") for data in spydata]
    proxies = []
    for rawdata in spydata:
        try:
            ip = rawdata.text.split("document")[0].split(" ")[1]
            port = rawdata.text.split(":")[-1]
            port = int(port)
            proxy = "{}:{}".format(ip, port)
            proxies.append(proxy)
        except:
            pass
    return proxies

def verify_proxies(proxies, timeout=4):
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Connection': 'keep-alive'
    }
    verified = []
    with requests.Session() as s:
        for proxy in proxies:
            httpproxy = {
                "http": "http://{}".format(proxy),
                "https": "https://{}".format(proxy),
            }
            try:
                p = s.get('http://icanhazip.com', headers=head, proxies=httpproxy, timeout=timeout)
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
                print("Connection/ReadTime timeout {}".format(proxy))
                continue
            except requests.exceptions.ProxyError:
                print("Proxy error: {}".format(proxy))
                continue
            print(proxy, p.text)
            if proxy.split(":")[0] == p.text.strip():
                verified.append(proxy)
            if len(verified) >= 5:
                break
        return verified

class Proxy(object):
    def __init__(self):
        self.update_proxies()

    def __iter__(self):
        return self

    def __next__(self): # Python 3: def __next__(self)
        if self.count >= self.max_count:
            # raise StopIteration
            self.update_proxies()
        else:
            self.count += 1
        return self.verified_proxies[self.count-1]

    def update_proxies(self):
        proxies = fetch_spys_proxies()
        verified_proxies = verify_proxies(proxies=proxies)
        self.verified_proxies = verified_proxies
        # self.verified_proxies = [1,2,3,5,4]
        self.count = 0
        self.max_count = len(self.verified_proxies) - 1

if __name__=="__main__":
    # proxies = fetch_spys_proxies()
    # verified_proxies = verify_proxies(proxies=proxies)
    # print()

    proxy = Proxy()
    print()
    # for p in proxy:
    #     print(p)