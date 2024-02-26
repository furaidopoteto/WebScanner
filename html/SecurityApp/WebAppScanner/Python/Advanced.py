import MySQLdb
import json
import atexit
# from selenium import webdriver
from seleniumwire import webdriver
from urllib.parse import urlparse
from time import sleep
from MySQLdb._exceptions import OperationalError
from urllib3.exceptions import MaxRetryError


def dbAndDriverclose(driver, conn, cur):
    conn.close
    cur.close
    driver.quit()


# 巡回したjsonのリクエスト情報をDBに保存する関数
def saveDB(json_urls, cur):
    json_str = [json.dumps(json_urls)]
    json_str = tuple(json_str)
    # SQL（データベースを操作するコマンド）を実行する
    sql = "UPDATE advanced SET json_urls=%s"
    cur.execute(sql, json_str)


# パラメータが完全に一致しているかを判定する関数
def parametercheck(reqdict, checkparams):
    flag = True
    checkparams = json.loads(checkparams)
    for key in reqdict.keys():
        reqparamsdict = json.loads(reqdict[key]["params"])
        for key2 in checkparams:
            if key2 not in reqparamsdict.keys():
                flag = False
    return flag            

if __name__ == '__main__':
    
    while True:
        try:
            # selenium-wireを使用してHTTPRequestHeaderを取得する 参考: https://pypi.org/project/selenium-wire/#description
            options = {
                'addr': 'apache'  # Address of the machine running Selenium Wire. Explicitly use 127.0.0.1 rather than localhost if remote session is running locally.
            }
            driver = webdriver.Remote(
                command_executor='http://selenium:4444/wd/hub',
                seleniumwire_options=options
            )
            break
        except MaxRetryError:
            print("接続失敗")
            sleep(1)
            continue


    print("接続成功")
    driver.get("https://google.com")


    while True:
        try:
            # DBから設定情報を取得する
            conn = MySQLdb.connect(
            user='root',
            passwd='furenntifuraizu',
            host='mysql',
            db='secapp',
            charset='utf8')
            # カーソルを取得する
            cur = conn.cursor()
            # SQL（データベースを操作するコマンド）を実行する
            sql = "SELECT domain, state, json_urls FROM advanced"
            cur.execute(sql)
        except OperationalError:
            sleep(2)
            continue
        
        atexit.register(dbAndDriverclose, driver, conn, cur)
        
        domain = None
        state = None
        json_urls = None
        # 実行結果を取得する
        rows = cur.fetchall()
        for row in rows:
            domain = row[0]
            state = row[1]
            json_urls = json.loads(row[2])
        
        
        # 診断対象を追加してもよい状態の場合はリクエストを分析してDBに保存する
        if state == "True":
            for request in driver.requests:
                METHOD = str(request.method).lower()
                URL = str(request.url)
                HEADERS = str(json.dumps(dict(request.headers)))
                STRHEADERS = str(request.headers)
                TYPE = str(request.headers['Content-Type'])
                try:
                    BODY = str(request.body.decode("utf-8"))
                except UnicodeDecodeError:
                    BODY = str(request.body)
                
                if(len(request.params.keys()) <= 0 and TYPE == "application/json"):
                    PARAMS = str(BODY)
                else:
                    PARAMS = str(json.dumps(request.params))
                

                # 指定されたドメインでContent-TypeがNone以外、またはクエリストリングがある場合は診断対象としてDBに保存する
                if request.response and domain in urlparse(URL).netloc:
                    # 取得したリクエストと同一のリクエストがすでに存在する場合はスキップする
                    sameflag = False
                    for reqdict in json_urls["requests"]:
                        requrl = list(reqdict.keys())[0]
                        if str(requrl).split("?")[0] == URL.split("?")[0] and parametercheck(reqdict, PARAMS):
                            sameflag = True
                    if sameflag:
                        continue
                    
                    if TYPE != 'None':
                        savedata = {URL: {"headers": HEADERS, "body": BODY, "strheaders": STRHEADERS, "method": METHOD, "content-type": TYPE, "params": PARAMS}}
                        json_urls["requests"].append(savedata)
                        saveDB(json_urls, cur)
                        # コミットしてデータを更新する(ちゃんとコミットしないと他コンテナには反映されない)
                        conn.commit()
                    elif "?" in URL:
                        savedata = {URL: {"headers": HEADERS, "body": BODY, "strheaders": STRHEADERS, "method": METHOD, "content-type": TYPE, "params": PARAMS}}
                        json_urls["requests"].append(savedata)
                        saveDB(json_urls, cur)
                        # コミットしてデータを更新する(ちゃんとコミットしないと他コンテナには反映されない)
                        conn.commit()
        else:
            break    
        del driver.requests
        sleep(2)
    
    