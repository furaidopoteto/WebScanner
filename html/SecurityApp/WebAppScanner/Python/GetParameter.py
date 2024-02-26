import bs4
import json
import sys
from time import sleep
from urllib.parse import unquote
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


if __name__ == '__main__':
    args = sys.argv # コマンドライン引数
    url = unquote(args[1])

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
    
    
    # 対象サイトのソースコードを解析して、使用されるパラメータを返す
    driver.get(url)
    html_text = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    
    forms = html_text.select("form")
    for i in forms:
        action = ""
        method = ""
        if("action" not in i.attrs):
            action = url
        else:
            action = urljoin(url, i.attrs["action"])
            if(i.attrs["action"] == ""):
                action = url
        nexturl = action
        if("method" not in i.attrs):
            method = "get"
        else:
            method = i.attrs["method"]
        inputs = i.select("input")
        textareas = i.select("textarea")
        selects = i.select("select")
        parameter = {}
        for j in inputs:
            if(j.attrs["type"] == "text" or j.attrs["type"] == "password" or j.attrs["type"] == "search"):
                parameter[j.attrs["name"]] =  ""
        for j in textareas:
            parameter[j.attrs["name"]] =  ""
        for j in selects:
            parameter[j.attrs["name"]] = ""
        parameter["method"] = method
        break

    print(json.dumps(parameter))
    
    # driverの解放
    driver.quit()