import MySQLdb
import json
import sys
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse

from Crawler import addnexturl
from Crawler import Login
from  CreateTransitionPDF import create_transition_img

if __name__ == "__main__":
    # chromedriverの設定

    options = Options()
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
    # ウィンドウサイズを最大化する 参考: https://qiita.com/studyinfra/items/bff92316baa4de1fedb5
    driver.maximize_window()
    
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

    loginpara = dict()
    loginurl = ""
    loginflagstr = ""
    loginflagpage = ""
    # 1行ずつ表示する
    for row in rows:
        loginpara = json.loads(row[0])
        loginurl = row[1]
        loginflagstr = row[2]
        loginflagpage = row[3]
    
    cur.close
    conn.close
    
    args = sys.argv # コマンドライン引数
    url = args[1]

    # 異なるオリジンに攻撃しないようオリジン名を保存しておく 参考: https://programmer-life.work/python/python-url-to-domain
    ORIGIN = urlparse(url).scheme+"://"+urlparse(url).netloc
    nexturls = [url]
    # 画面遷移用の連想配列の定義
    associative_array = {url.replace(ORIGIN, ""): []}
    
    start_time = datetime.datetime.now()
    driver = Login(loginurl, driver, loginpara, start_time, ORIGIN)
    
    # 画面遷移図用のスクショを保存する連想配列
    pdfimages = {}
    
    # 戻り値を受け取るための変数
    temp = {}
    
    # クローラを起動して画面遷移図用の連想配列を生成する
    nexturls, associative_array, pdfimages, ScreenTitle, temp = addnexturl(url, nexturls, ORIGIN, driver, loginurl, loginpara, start_time, associative_array, pdfimages, 0, True, loginflagstr=loginflagstr, loginflagpage=loginflagpage)
    
    # ドライバーのメモリ解法
    driver.quit()
    
    # 画面遷移図の作成
    ZIPFILEPATH = create_transition_img(associative_array, ORIGIN, loginurl, loginpara, 0, True, pdfimages, url, ScreenTitle)
    print(ZIPFILEPATH)