import json
import sys
import MySQLdb
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse

from Crawler import addnexturl
from Crawler import Login
from Crawler import GetrobotsAndsitemap

TIMEOUT_SEC = 5*60

if __name__ == '__main__':
    # chromedriverの設定
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
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
    sql = "SELECT loginpara_json, loginurl, loginflagstr, loginflagpage FROM scannersetting"
    cur.execute(sql)

    # 実行結果を取得する
    rows = cur.fetchall()

    cur.close
    conn.close
    
    args = sys.argv # コマンドライン引数
    url = args[1]

    loginpara = {}
    loginurl = ""
    loginflagstr = ""
    loginflagpage = ""
    # 1行ずつ表示する
    for row in rows:
        loginpara = json.loads(row[0])
        loginurl = row[1]
        loginflagstr = row[2]
        loginflagpage = row[3]

    # 異なるオリジンに攻撃しないようオリジン名を保存しておく 参考: https://programmer-life.work/python/python-url-to-domain
    ORIGIN = urlparse(url).scheme+"://"+urlparse(url).netloc
    nexturls = [url]

    start_time = datetime.datetime.now()
    driver = Login(loginurl, driver, loginpara, start_time, ORIGIN)
    # 画面遷移用の連想配列の定義
    associative_array = {url.replace(ORIGIN, ""): []}
    
    # 画面遷移図用の画像を保存するための連想配列
    pdfimages  = {}
    
    # 戻り値を受け取るための変数
    temp = {}

    
    # nexturls変数にurl変数から遷移可能な全てのURLをnexturlsの配列に格納する
    nexturls, associative_array, pdfimages, temp, temp2 = addnexturl(url, nexturls, ORIGIN, driver, loginurl, loginpara, start_time, associative_array, pdfimages, 0, False, loginflagstr=loginflagstr, loginflagpage=loginflagpage)
    
    session = requests.session()
    
    # robots.txtファイルやsitemap.xmlからもURLを抽出する
    nexturls = GetrobotsAndsitemap(driver, session, ORIGIN, nexturls, associative_array)

    print(json.dumps(nexturls))
    driver.quit()