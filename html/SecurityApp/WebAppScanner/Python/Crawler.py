import json
import bs4
import re
import datetime
import requests
import uuid
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import JavascriptException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import UnexpectedAlertPresentException
from urllib.parse import parse_qs
from urllib.parse import urlparse
from urllib.parse import urljoin
from Operation import *

TIMEOUT_SEC = 5*60
searchurls = []

KEYVALUES = {"email": "demodata@demodata.com", "mail": "demodata@demodata.com", "tel": "012-3456-7890", "number": "0", "url": "https://localhost"}


# ログイン情報をもとにログインする関数
def Login(loginurl, driver, loginpara, start_time, ORIGIN):
    td = datetime.datetime.now() - start_time
    if(td.seconds >= TIMEOUT_SEC):
        print("タイムアウト")
        return driver

    if(loginurl != "" and OriginCheck(loginurl, ORIGIN)):
        # seleniumでログイン情報を入力してセッションを確立
        driver.get(loginurl)
        for inputtag in driver.find_elements_by_css_selector("input[type='hidden']"):
            nameattribute = inputtag.get_attribute("name")
            if(nameattribute != None and not nameattribute in loginpara.keys()):
                val = inputtag.get_attribute("value")
                driver.execute_script("document.getElementsByName(`"+nameattribute+"`)[0].setAttribute('value', `"+val+"`)")
        element = None
        for i in loginpara.keys():
            element = driver.find_element_by_name(i)
            element.send_keys(loginpara[i])
        element.submit()
    return driver

# 画面遷移図用の連想配列にページを追加する関数
def addassociative_array(nexturl, associative_array, newpath, ORIGIN, ScreenShotFlag, pdfimages, ScreenTitle, SCANID, driver):
    # 画面遷移図用の変数に元のURLに対する遷移先を配列として追加していく
    urlkey = str(nexturl).replace(ORIGIN, "")
    if(urlkey in associative_array):
        associative_array[urlkey].append(str(newpath).replace(ORIGIN, ""))
    else:
        associative_array[urlkey] = [str(newpath).replace(ORIGIN, "")]
    
    if(ScreenShotFlag and newpath not in pdfimages.keys()):
        # 画面遷移図用にスクショを撮影する
        pdfimages, ScreenTitle = ScreenShot(SCANID, driver, pdfimages, newpath, ScreenTitle)
    return associative_array, pdfimages, ScreenTitle

# 画面遷移図用のスクショを撮影して、画像ファイルとして保存する関数
def ScreenShot(SCANID, driver, pdfimages, newpath, ScreenTitle):
    try:
        os.mkdir("./Python/TransitionImages/"+str(SCANID))
    except FileExistsError:
        pass
    filepath = "./Python/TransitionImages/"+str(SCANID)+"/"+str(uuid.uuid4())+".png"
    
    w = 1500
    h = 1000
    driver.set_window_size(w, h)
    
    # Get Screen Shot
    driver.save_screenshot(filepath)
    
    pdfimages[newpath] = filepath.replace("./Python/", "../")
    ScreenTitle[newpath] = driver.title
    return pdfimages, ScreenTitle


# 格納型XSSでアラートが発生している場合driverの操作ができないのでそれを検査する関数
def AlertCheck(driver):
    try:
        driver.find_elements_by_css_selector("input[type='hidden']")
    except UnexpectedAlertPresentException:
        # 格納型XSSなど複数アラートが表示される場合があるのですべて削除する
        while(True):
            try:
                Alert(driver).accept()
            except NoAlertPresentException:
                break
    return driver


# 収集したパスの中から同じkeyのクエリストリングを除外する関数
def QueryStrCheck(PATHS, ALLPATHS, nexturl, attr):
    tmppaths = {}
    for path in PATHS:
        # 同じURLかつGETパラメータが同一の場合はスキップする
        newpath = urljoin(nexturl, path.get(f"{attr}"))
        noquerystrpath = newpath[:str(newpath).find("?")]
        getpara = parse_qs(urlparse(newpath).query)
        # flagがTrueの場合は、URLまたはGETパラメータが重複していないのでリストに追加する
        flag = True
        if(noquerystrpath in tmppaths):
            flag = False
            # GETパラメータを一つずつチェックしていき一つでも異なるパラメータが存在した場合はリストに追加する
            for key in getpara.keys():
                for para in tmppaths[noquerystrpath]:
                    if(key not in para):
                        flag = True
        
        if("?" in path.get(f"{attr}") and flag):
            ALLPATHS.append(path.get(f"{attr}"))
            if(noquerystrpath in tmppaths):
                tmppaths[noquerystrpath].append(getpara)
            else:
                tmppaths[noquerystrpath] = []
    
    return ALLPATHS


def OriginCheck(pageurl, ORIGIN):
    if(pageurl.startswith(ORIGIN)):
        return True
    else:
        return False

def urlCheck(pageurl):
    pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    if(re.match(pattern, pageurl)):
        return True
    else:
        return False

def GetrobotsAndsitemap(driver, session, ORIGIN, nexturls, associative_array):
    # robots.txtファイルの中身からもURLを抽出する
    response = session.get(ORIGIN+"/robots.txt")
    txt = response.text
    pattern = "https?://[A-Za-z0-9_/:%#$&?()~.=+-]+?(?=https?:|[^A-Za-z0-9_/:%#$&?()~.=+-]|$)"
    for robotsurl in txt.split(": "):
        if("User-agen" not in txt or response.status_code == 404):
            break
        if("*" in robotsurl):
            continue
        if("User-agent" in robotsurl):
            continue
        robotsurl = robotsurl.replace("Disallow", "").replace("Sitemap", "").replace("Allow", "")
    
        # sitemap.xmlがある場合はそのファイルにアクセスしてlocタグ内のURLを抽出する
        if("sitemap.xml" in robotsurl):
            href = urljoin(ORIGIN, robotsurl)
            if(OriginCheck(href, ORIGIN)):
                response = session.get(href)
                html_text = bs4.BeautifulSoup(response.text, "html.parser")
                loctags = html_text.find_all("loc")
                for loctag in loctags:
                    if(OriginCheck(loctag.text, ORIGIN)):
                        associative_array['sitemap.xml'] = loctag
                        nexturls.append(loctag.text)
            
            
        if(re.match(pattern, robotsurl)):
            href = robotsurl.replace("\n", "")
            if(OriginCheck(robotsurl, ORIGIN)):
                res = session.get(robotsurl)
                if(res.status_code == 404):
                    continue
                href = res.url
                if(href in nexturls or not href.startswith(ORIGIN)):
                    continue
                else:
                    nexturls.append(href)
        else:
            href = urljoin(ORIGIN, robotsurl)
            if(OriginCheck(href, ORIGIN)):
                res = session.get(href)
                if(res.status_code == 404):
                    continue
                href = res.url
                if(href in nexturls or not href.startswith(ORIGIN)):
                    continue
                else:
                    nexturls.append(href)
    return nexturls


# ドライバのメモリを解放する関数
def driverquit(driver):
    driver.quit()    


# 新たにドライバを生成する関数
def createdriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    driver2 = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
    return driver2


# 対象サイトを巡回して遷移可能な全てのURLを収集する
def addnexturl(nexturl, nexturls, ORIGIN, driver, loginurl, loginpara, start_time, associative_array, pdfimages, SCANID, ScreenShotFlag, loginflagstr="", loginflagpage="", ScreenTitle={}, StepActions={}):
    global searchurls
    
    
    td = datetime.datetime.now() - start_time
    if(td.seconds >= TIMEOUT_SEC):
        print("タイムアウト")
        # nexturlsの重複の排除
        tmpdict = dict.fromkeys(nexturls)
        nexturls = list(tmpdict)
        return nexturls, associative_array, pdfimages, ScreenTitle, StepActions
    # ページが更新されたり閉じたりしたら強制終了する
    haitacheck = requests.post("http://127.0.0.1/SecurityApp/WebAppScanner/HaitaCheck.php", {"check": "yes"})
    if(haitacheck.text == "NotReady"):
        # NotReadyをReadyに戻してDBをリセットして強制終了
        requests.post("http://127.0.0.1/SecurityApp/WebAppScanner/HaitaCheck.php", {"check": "no"})
        AttackInfoReset()
        driver.quit()
        exit(0)
    
    
    if(not OriginCheck(nexturl, ORIGIN)):
        return nexturls, associative_array, pdfimages, ScreenTitle, StepActions
    # formでの遷移の場合再度アクセスするとセッションが途切れてしまう可能性があるのでnexturlと現在のURLが異なる場合のみ遷移する
    if(not driver.current_url == nexturl): 
        driver.get(nexturl)
    realurl = driver.current_url
    
    # リダイレクトされ既に探索済みのURLだった場合は遷移図だけ記録してこれ以上は探索しないようにする
    if(realurl in nexturls and realurl != nexturl and realurl in searchurls):
        return nexturls, associative_array, pdfimages, ScreenTitle, StepActions
    
    # ページのURLを収集する前にformがある場合はsubmitする(確認画面などの可能性があるから)
    # form内を入力してsubmitした後の遷移先を収集する
    ActionElement = driver.find_elements_by_css_selector("[action]")
    # ActionElementそのものを使用するのではなく現在の添え字で指定することで、古い要素を参照することで起きるエラーを回避する
    for index in range(len(ActionElement)):
        # addnexturlを実行した後はdriverのページが変わってしまうのでリセットする
        if(not driver.current_url == nexturl): 
            driver.get(nexturl)
        realurl = driver.current_url
        
        if(not OriginCheck(driver.current_url, ORIGIN)):
            continue
        
        if(realurl != loginurl):
            # 入力欄を取得してsubmitする
            ActionElement = driver.find_elements_by_css_selector("[action]")
            inputs = ActionElement[index].find_elements_by_css_selector("input")
            textareas = ActionElement[index].find_elements_by_css_selector("textarea")
            selects = ActionElement[index].find_elements_by_css_selector("select")
            tmp = None
            TaikaiFlag = False
            for input in inputs:
                tmp = input
                attr = input.get_attribute("type")
                name = input.get_attribute("name")
                value = input.get_attribute("value")
                sendval = "demodata"
                if(attr in KEYVALUES):
                    sendval = KEYVALUES[attr]
                elif(name in KEYVALUES):
                    sendval = KEYVALUES[name]
                # ログイン用のアカウントが削除されてしまう問題の応急処置
                if(value == "退会" or value == "アカウント削除"):
                    TaikaiFlag = True
                try:
                    if(attr == "date"):
                        driver.execute_script(f'document.getElementsByClassName(`{input.get_attribute("name")}`).value=`{datetime.datetime.now().strftime("%Y-%m-%d")}`;')
                    elif(attr == "file"):
                        input.send_keys("/var/www/html/SecurityApp/WebAppScanner/Python/DemoUploadFile/win3.jpg")
                    else:
                        input.send_keys(sendval)
                except ElementNotInteractableException:
                    continue
            try:
                for element in textareas:
                    tmp = element
                    element.send_keys("demodata")
                for element in selects:
                    tmp = element
                    select = Select(element)
                    select.select_by_index(0)
            except ElementNotInteractableException:
                continue
            
            # 退会やアカウント削除だった場合はsubmitせずにループを抜ける
            if(TaikaiFlag):
                continue
            tmp.submit()
        else:
            driver = Login(loginurl, driver, loginpara, start_time, ORIGIN)
        
        # submit時にアラートを発するアプリがあるので解除してからurlを取得する
        driver = AlertCheck(driver)
        newpath = driver.current_url
        if(not OriginCheck(newpath, ORIGIN)):
            continue
        if(newpath in nexturls):
            # associative_array, pdfimages, ScreenTitle = addassociative_array(nexturl, associative_array, newpath, ORIGIN, ScreenShotFlag, pdfimages, ScreenTitle, SCANID, driver)
            continue
        # 同一URLでクエリストリングが違う場合は検査ページを限定する
        querycount = 0
        sharpcount = 0
        for url in nexturls:
            if(("?" in url and "?" in newpath) and url[:str(url).find("?")] == newpath[:str(newpath).find("?")]):
                querycount += 1
            if(("#" in newpath)):
                sharpcount += 1
        if(querycount >= 1 or sharpcount >= 1):
            continue
        
        # 同一オリジンのURLだけ抽出
        if(OriginCheck(newpath, ORIGIN)):
            if(newpath in nexturls):
                continue
            nexturls.append(newpath)
            associative_array, pdfimages, ScreenTitle = addassociative_array(nexturl, associative_array, newpath, ORIGIN, ScreenShotFlag, pdfimages, ScreenTitle, SCANID, driver)
            
            if(ScreenShotFlag and newpath not in pdfimages.keys()):
                # 画面遷移図用にスクショを撮影する
                pdfimages, ScreenTitle = ScreenShot(SCANID, driver, pdfimages, newpath, ScreenTitle)
            
            
            # 別ドライバを生成して段階アクセスが必要かを調べる
            driver2 = createdriver()
            # 段階を経てアクセスするページかを検証する
            driver2 = Login(loginurl, driver2, loginpara, start_time, ORIGIN)
            # 二つ目のクローラで段階を踏まずにアクセスできるか検証する
            driver2.get(newpath)
            driver2url = driver2.current_url
            if(driver2url != newpath):
                # 段階を踏まないとアクセスできないページの組み合わせを
                # 連想配列として保存する
                if(realurl in StepActions):
                    StepActions[realurl].append(newpath)
                else:
                    StepActions[realurl] = []
                    StepActions[realurl].append(newpath)
            # driver2のメモリを解放する
            driverquit(driver2)
                
            # フォームでしか移動できないページのhref属性(遷移先)を調べて画面遷移図に反映させる
            html_text2 = bs4.BeautifulSoup(driver.page_source, 'html.parser')
            driverurl = driver.current_url
            for element in html_text2.select("a, button", limit=30):
                href = urljoin(driverurl, element.get("href"))
                if(not OriginCheck(href, ORIGIN)):
                    continue
                if(href in nexturls):
                    associative_array, pdfimages, ScreenTitle = addassociative_array(newpath, associative_array, href, ORIGIN, False, pdfimages, ScreenTitle, SCANID, driver2)
                    continue
            ButtonsCrawler(driver, html_text2, driverurl, ORIGIN, nexturls, ScreenShotFlag, SCANID, loginflagpage, loginurl, loginflagstr, loginpara, start_time, associative_array, pdfimages, ScreenTitle, StepActions)
            
            
            SaveDB("巡回中", "", "", 0, 0, "0.0%", 0, json.dumps({"urls": nexturls}))
            # print(newpath)
            
            
            # クローリング中にログアウトしてしまったかどうかを確認して再度ログインする
            if(loginflagpage != "" and OriginCheck(loginflagpage, ORIGIN)):
                driver.get(loginflagpage)
                page_source = driver.page_source
            else:
                page_source = ""
            if(loginurl != "" and loginflagstr not in page_source):
                driver = Login(loginurl, driver, loginpara, start_time, ORIGIN)
                
            addnexturl(newpath, nexturls, ORIGIN, driver, loginurl, loginpara, start_time, associative_array, pdfimages, SCANID, ScreenShotFlag, loginflagstr=loginflagstr, loginflagpage=loginflagpage, ScreenTitle=ScreenTitle, StepActions=StepActions)
    
    # クローリング中にログアウトしてしまったかどうかを確認して再度ログインする
    if(loginflagpage != "" and OriginCheck(loginflagpage, ORIGIN)):
        driver.get(loginflagpage)
        page_source = driver.page_source
    else:
        page_source = ""
    if(loginurl != "" and loginflagstr not in page_source):
        driver = Login(loginurl, driver, loginpara, start_time, ORIGIN)
    # formでの遷移の場合再度アクセスするとセッションが途切れてしまう可能性があるのでnexturlと現在のURLが異なる場合のみ遷移する
    if(not driver.current_url == nexturl):
        driver.get(nexturl)
    # Formの操作をしている時に元のページに戻れなくなった場合はこれ以上調べない
    if(realurl != driver.current_url):
        return nexturls, associative_array, pdfimages, ScreenTitle, StepActions 

    driver = AlertCheck(driver)
    html_text = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    
    if(not OriginCheck(realurl, ORIGIN)):
        return nexturls, associative_array, pdfimages, ScreenTitle, StepActions
    # 属性値のクエリストリングも巡回先として収集する
    SRCPATHS = html_text.select("[src]", limit=30)
    ALLPATHS = list()
    
    
    ALLPATHS = QueryStrCheck(SRCPATHS, ALLPATHS, nexturl, "src")
                
    
    for path in ALLPATHS:
        newpath = urljoin(nexturl, path)
        if(not OriginCheck(newpath, ORIGIN)):
            continue
        driver.get(newpath)
        driver = AlertCheck(driver)
        newpath = driver.current_url
        # 同一URLでクエリストリングが違う場合は検査ページを限定する
        querycount = 0
        sharpcount = 0
        for url in nexturls:
            if(("?" in url and "?" in newpath) and url[:str(url).find("?")] == newpath[:str(newpath).find("?")]):
                querycount += 1
            if(("#" in newpath)):
                sharpcount += 1
        if(querycount >= 1 or sharpcount >= 1):
            continue
        if(newpath in nexturls):
            # associative_array, pdfimages, ScreenTitle = addassociative_array(nexturl, associative_array, newpath, ORIGIN, ScreenShotFlag, pdfimages, ScreenTitle, SCANID, driver)
            continue
        # 同一オリジンのURLだけ抽出
        if(newpath.startswith(ORIGIN)):
            if(newpath in nexturls):
                continue
            nexturls.append(newpath)
            associative_array, pdfimages, ScreenTitle = addassociative_array(nexturl, associative_array, newpath, ORIGIN, ScreenShotFlag, pdfimages, ScreenTitle, SCANID, driver)
            
            if(ScreenShotFlag and newpath not in pdfimages.keys()):
                # 画面遷移図用にスクショを撮影する
                pdfimages, ScreenTitle = ScreenShot(SCANID, driver, pdfimages, newpath, ScreenTitle)
            
            SaveDB("巡回中", "", "", 0, 0, "0.0%", 0, json.dumps({"urls": nexturls}))
            # print(newpath)
            # クローリング中にログアウトしてしまったかどうかを確認して再度ログインする
            if(loginflagpage != "" and OriginCheck(loginflagpage, ORIGIN)):
                driver.get(loginflagpage)
                page_source = driver.page_source
            else:
                page_source = ""
            if(loginurl != "" and loginflagstr not in page_source):
                driver = Login(loginurl, driver, loginpara, start_time, ORIGIN)
            addnexturl(newpath, nexturls, ORIGIN, driver, loginurl, loginpara, start_time, associative_array, pdfimages, SCANID, ScreenShotFlag, loginflagstr=loginflagstr, loginflagpage=loginflagpage, ScreenTitle=ScreenTitle, StepActions=StepActions)
        

    # クローリング中にログアウトしてしまったかどうかを確認して再度ログインする
    if(loginflagpage != "" and OriginCheck(loginflagpage, ORIGIN)):
        driver.get(loginflagpage)
        page_source = driver.page_source
    else:
        page_source = ""
    if(loginurl != "" and loginflagstr not in page_source):
        driver = Login(loginurl, driver, loginpara, start_time, ORIGIN)
    
    if(not driver.current_url == nexturl):
        driver.get(nexturl)
    
    
    # Formの操作をしている時に元のページに戻れなくなった場合はこれ以上調べない
    if(realurl != driver.current_url):
        return nexturls, associative_array, pdfimages, ScreenTitle, StepActions 
    
    if(len(html_text.select("a")) <= 0 and len(html_text.select("button")) <= 0 and len(html_text.select("[action]")) <= 0):
        # nexturlsの重複の排除
        tmpdict = dict.fromkeys(nexturls)
        nexturls = list(tmpdict)
        return nexturls, associative_array, pdfimages, ScreenTitle, StepActions
    
    # aタグやbuttonタグの探索を行う
    ButtonsCrawler(driver, html_text, nexturl, ORIGIN, nexturls, ScreenShotFlag, SCANID, loginflagpage, loginurl, loginflagstr, loginpara, start_time, associative_array, pdfimages, ScreenTitle, StepActions)
    searchurls.append(nexturl)
    
    # nexturlsの重複の排除
    tmpdict = dict.fromkeys(nexturls)
    nexturls = list(tmpdict)
    return nexturls, associative_array, pdfimages, ScreenTitle, StepActions


# aタグやbuttonタグの属性や実際にクリックすることで探索を行う関数
def ButtonsCrawler(driver, html_text, nexturl, ORIGIN, nexturls, ScreenShotFlag, SCANID, loginflagpage, loginurl, loginflagstr, loginpara, start_time, associative_array, pdfimages, ScreenTitle, StepActions):
    # 対象URLから同一オリジンの遷移先を配列にまとめる
    pages = []
    
    # 現在全てのボタンを探索しており、巡回に時間がかかってしまっているので、同じURLでGETパラメータも重複してる場合は除外する処理の作成途中
    allpaths = []
    tmpallpaths = []
    for element in html_text.select("a, button", limit=30):
        href = urljoin(nexturl, element.get("href"))
        if(not OriginCheck(href, ORIGIN)):
            continue
        if(href in nexturls):
            associative_array, pdfimages, ScreenTitle = addassociative_array(nexturl, associative_array, href, ORIGIN, False, pdfimages, ScreenTitle, SCANID, driver)
            continue
        if(href == None):
            continue
        allpaths.append(element)
    
    tmpallpaths = allpaths.copy()
            
    for url in nexturls:
        for element in tmpallpaths:
            href = element.get("href")
            flag = True
            # URLにGETパラメータが存在し、かつパラメータを除外したURLが一致した場合はパラメータも同一なのかを検査する
            if(("?" in url and "?" in href) and url[:str(url).find("?")] == href[:str(href).find("?")]):
                getpara1 = parse_qs(urlparse(url).query)
                getpara2 = parse_qs(urlparse(href).query)
                cnt = 0
                for key1 in getpara1.keys():
                    if(key1 in getpara2):
                        cnt += 1
                if(cnt == len(getpara1.keys()) and len(getpara1.keys()) == len(getpara2.keys())):
                    flag = False
            # 抽出したhref属性のURLとパラメータ名が同一の場合は除外する
            if(not flag):
                allpaths.remove(element)
            else:
                continue
    
    
    for element in allpaths:
        # クローリング中にログアウトしてしまったかどうかを確認して再度ログインする
        if(loginflagpage != "" and OriginCheck(loginflagpage, ORIGIN)):
            driver.get(loginflagpage)
            page_source = driver.page_source
        else:
            page_source = ""
        if(loginurl != "" and loginflagstr not in page_source):
            driver = Login(loginurl, driver, loginpara, start_time, ORIGIN)
        # ページをリセット
        driver.get(nexturl)
        
        tmpurl = urljoin(nexturl, element.get("href"))
        if(not OriginCheck(driver.current_url, ORIGIN) or not OriginCheck(tmpurl, ORIGIN)):
            continue
        text = element.text
        # ログイン用のアカウントが削除されてしまう問題の応急処置
        if(text == "退会" or text == "アカウント削除"):
            continue
        # URLが画像のダウンロードだった場合はスキップする
        if(urlCheck(tmpurl)):
            response = requests.get(tmpurl)
        else:
            continue
        
        if("?" not in tmpurl and "Content-Type" in response.headers):
            if("image" in response.headers["Content-Type"]):
                continue
        # すでにアクセスしたURLと全く同じ場合はスキップする
        if(tmpurl in pages):
            continue
        else:
            pages.append(tmpurl)
        # href属性にjavascriptスキームがある場合は要素をクリックして遷移先のURLを収集
        if(element.get("href") != None and re.search("^javascript:", element.get("href"))):
            # アラートダイアログが表示された状態でJavaScriptを実行すると例外が発生するので
            # Alert(driver).accept()でアラートが表示されている場合は閉じる 参考: https://blog.ikedaosushi.com/entry/2019/01/18/232326 | https://teratail.com/questions/201673
            try:
                driver.execute_script(element.get("href"))
                Alert(driver).accept()
                href = driver.current_url
            except NoAlertPresentException:
                href = driver.current_url
        elif(element.get("onclick") != None):
            try:
                driver.execute_script(element.get("onclick"))
                Alert(driver).accept()
                href = driver.current_url
            except NoAlertPresentException:
                href = driver.current_url
            except JavascriptException:
                href = driver.current_url
        else:
            href = urljoin(nexturl, element.get("href"))
        
        
        if(not OriginCheck(href, ORIGIN)):
            continue
        driver.get(href)
        driver = AlertCheck(driver)
        href = driver.current_url
        if(href in nexturls):
            associative_array, pdfimages, ScreenTitle = addassociative_array(nexturl, associative_array, href, ORIGIN, False, pdfimages, ScreenTitle, SCANID, driver)
            continue
        # 同一URLでクエリストリングが違う場合は検査ページを限定する
        querycount = 0
        sharpcount = 0
        for url in nexturls:
            if(("?" in url and "?" in href) and url[:str(url).find("?")] == href[:str(href).find("?")]):
                querycount += 1
            if(("#" in href)):
                sharpcount += 1
        if(querycount >= 1 or sharpcount >= 1):
            continue
        # 同一オリジンのURLだけ抽出
        if(href.startswith(ORIGIN)):
            if(href in nexturls):
                # associative_array, pdfimages, ScreenTitle = addassociative_array(nexturl, associative_array, href, ORIGIN, ScreenShotFlag, pdfimages, ScreenTitle, SCANID, driver)
                continue
            nexturls.append(href)
            associative_array, pdfimages, ScreenTitle = addassociative_array(nexturl, associative_array, href, ORIGIN, ScreenShotFlag, pdfimages, ScreenTitle, SCANID, driver)
            
            if(ScreenShotFlag and href not in pdfimages.keys()):
                # 画面遷移図用にスクショを撮影する
                pdfimages, ScreenTitle = ScreenShot(SCANID, driver, pdfimages, href, ScreenTitle)
                
            # print(href)
            SaveDB("巡回中", "", "", 0, 0, "0.0%", 0, json.dumps({"urls": nexturls}))
            # クローリング中にログアウトしてしまったかどうかを確認して再度ログインする
            if(loginflagpage != "" and OriginCheck(loginflagpage, ORIGIN)):
                driver.get(loginflagpage)
                page_source = driver.page_source
            else:
                page_source = ""
            if(loginurl != "" and loginflagstr not in page_source):
                driver = Login(loginurl, driver, loginpara, start_time, ORIGIN)
            addnexturl(href, nexturls, ORIGIN, driver, loginurl, loginpara, start_time, associative_array, pdfimages, SCANID, ScreenShotFlag, loginflagstr=loginflagstr, loginflagpage=loginflagpage, ScreenTitle=ScreenTitle, StepActions=StepActions)