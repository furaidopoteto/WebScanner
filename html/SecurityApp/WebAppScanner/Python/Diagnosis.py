import requests
import bs4
import json
import sys
import re
import os
import MySQLdb
import datetime
import uuid
from time import sleep
from requests.exceptions import Timeout
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import parse_qs
from urllib.parse import unquote
from urllib3.exceptions import LocationParseError
from requests.exceptions import ConnectionError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import UnexpectedAlertPresentException
from requests import Response

from http.client import RemoteDisconnected

from Crawler import addnexturl
from Crawler import ScreenShot
from Crawler import GetrobotsAndsitemap
from Crawler import AlertCheck
from  CreateTransitionPDF import create_transition_img
from Operation import *

KEYVALUES = {"email": "demodata@demodata.com", "mail": "demodata@demodata.com", "tel": "012-3456-7890", "number": "0", "url": "https://localhost"}

ANGULARPATTER = [r"{{$on.constructor('alert(1)')()}}", r"{{constructor.constructor('alert(1)')()}}"]


# パターンの初期化
def SetPattern():
    with open('./WordListFiles/SQLInjection.txt', encoding="utf-8") as f:
        for line in f:
            SQLINJECTION.append(str(line).replace("\n", ""))
    
    with open('./WordListFiles/XSS.txt', encoding="utf-8") as f:
        for line in f:
            XSS.append(str(line).replace("\n", ""))

    with open('./WordListFiles/OScommand.txt', encoding="utf-8") as f:
        for line in f:
            OSCOMMAND.append(str(line).replace("\n", ""))

    with open('./WordListFiles/Dir_Traversal.txt', encoding="utf-8") as f:
        for line in f:
            DIR_TRAVERSAL.append(str(line).replace("\n", ""))

    with open('./WordListFiles/OpenRedirect.txt', encoding="utf-8") as f:
        for line in f:
            OPEN_REDIRECT.append(str(line).replace("\n", ""))
    
    with open('./WordListFiles/HTTPHeaderInjection.txt', encoding="utf-8") as f:
        for line in f:
            HTTP_HEADERINJECTION.append(str(line).replace("\n", ""))


def Login(driver, session, loginurl, loginpara):
    if(loginurl != ""):
        driver = AlertCheck(driver)
        # seleniumでログイン情報を入力してセッションを確立
        driver.get(loginurl)
        for inputtag in driver.find_elements_by_css_selector("input[type='hidden']"):
            nameattribute = inputtag.get_attribute("name")
            if(nameattribute != None and not nameattribute in loginpara.keys()):
                val = inputtag.get_attribute("value")
                driver.execute_script(f"document.getElementsByName(`{nameattribute}`)[0].setAttribute('value', `{val}`)")
        element = None
        for i in loginpara.keys():
            element = driver.find_element_by_name(i)
            element.send_keys(loginpara[i])
        element.submit()
        
        
        driver = AlertCheck(driver)
        #セッションの受け渡し
        for cookie in driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"])
        
    return driver, session


# session変数のCookieをdriverにコピーする関数
def SessionCopyToDriver(session, driver):
    cookies = session.cookies.get_dict()
    for cookiename in cookies:
        driver.add_cookie({"name": cookiename, "value": cookies[cookiename]})
    
    return driver
    


# 脆弱性が見つかった時に詳細データを配列に格納する関数
def AddAttackData(CheckAttack, requesturl, requestmotourl, result, pattern, Method, filepath=""):
    requestURLs[formnum][CheckAttack].append(requesturl)
    requestMotoURLs[formnum][CheckAttack].append(requestmotourl)
    requestMethods[formnum][CheckAttack].append(Method)
    responseErrortexts[formnum][CheckAttack].append(result)
    AttackParameters[formnum][CheckAttack].append(pattern)
    ScreenShot[formnum][CheckAttack].append(filepath)
    Errorcounts[formnum][CheckAttack] += 1


def AddHeaderData(checkheader, requesturl, requestmotourl, responseheader, checksession, Method):
    HeaderAlertCount[formnum][checkheader] += 1
    HeaderAlertURLs[formnum][checkheader].append(requesturl)
    HeaderAlertMotoURLs[formnum][checkheader].append(requestmotourl)
    HeaderAlertMethods[formnum][checkheader].append(Method)
    if(checksession):
        HeaderAlertText[formnum][checkheader].append(responseheader["Set-Cookie"])
    else:
        HeaderAlertText[formnum][checkheader].append("")


# 脆弱性の詳細データを保存するための辞書を1つ配列に追加する関数(フォームごとにデータを分けるため)
def AddDictData():
    # 脆弱性を発見したときのリクエスト先URL・レスポンス文字列・攻撃コード・攻撃名と発見した数の辞書 を格納するための変数
    # [{"攻撃名": [パラメータ...], "攻撃名": [パラメータ...]}, {"攻撃名": [パラメータ...], "攻撃名": [パラメータ...]}]
    # という構造になっており、外側の配列はformnumでフォームごとに分けて、フォームごと・攻撃ごとのパラメータで分けて使用する
    tmp1 = {}
    tmp2 = {}
    tmp3 = {}
    tmp4 = {}
    tmp5 = {}
    tmp6 = {}
    tmp7 = {}
    for i in ATTACK_NAME:
        tmp1.update({i: 0})
        tmp2.update({i: []})
        tmp3.update({i: []})
        tmp4.update({i: []})
        tmp5.update({i: []})
        tmp6.update({i: []})
        tmp7.update({i: []})
    Errorcounts.append(tmp1)
    requestURLs.append(tmp2)
    responseErrortexts.append(tmp3)
    AttackParameters.append(tmp4)
    requestMotoURLs.append(tmp5)
    requestMethods.append(tmp6)
    ScreenShot.append(tmp7)

    # 推奨されているヘッダーがなかったURLと属性ごとの検出数を格納する変数
    tmp1 = {}
    tmp2 = {}
    tmp3 = {}
    tmp4 = {}
    tmp5 = {}
    for i in PHPSESSID_CHECK:
        tmp1.update({i: 0})
        tmp2.update({i: []})
        tmp3.update({i: []})
        tmp4.update({i: []})
        tmp5.update({i: []})
    for i in CHECK_RESPONSE_HEADERS:
        tmp1.update({i: 0})
        tmp2.update({i: []})
        tmp3.update({i: []})
        tmp4.update({i: []})
        tmp5.update({i: []})
    HeaderAlertCount.append(tmp1)
    HeaderAlertURLs.append(tmp2)
    HeaderAlertMotoURLs.append(tmp3)
    HeaderAlertText.append(tmp4)
    HeaderAlertMethods.append(tmp5)

# 受け取ったdriverをスクショして画像ファイルを保存する
def DriverScreenShot(CheckAttack):
    w = driver.execute_script("return document.body.scrollWidth;")
    h = driver.execute_script("return document.body.scrollHeight;")

    # set window size
    driver.set_window_size(w,h)
    
    try:
        os.mkdir("./images/"+str(SCANID))
    except FileExistsError:
        pass

    filepath = "./images/"+str(SCANID)+"/"+str(CheckAttack)+str(uuid.uuid4())+".png"
    # Get Screen Shot
    driver.save_screenshot(filepath)
    
    # ウィンドウサイズをもとに戻す
    driver.maximize_window()
    
    return filepath

# エラー画面のスクショを保存する関数 参考: https://qiita.com/DisneyAladdin/items/431e9fd0c1cf709347da
def ErrorScreenShot(pattern, requestmotourl, CheckAttack, Method, GETMethodURL):
    if(not CheckAttack == "オープンリダイレクト"):
        if(str(Method).lower() == "get"):
            driver.get(GETMethodURL)
        else:    
            driver.get(requestmotourl)
            # 格納型XSSなど複数アラートが表示される場合があるのですべて削除する
            while(True):
                try:
                    Alert(driver).accept()
                except NoAlertPresentException:
                    break
            if(pattern != ""):
                pattern_dict = json.loads(pattern)
                for name in pattern_dict.keys():
                    val = pattern_dict[name]
                    elements = driver.find_elements_by_name(name)
                    tmp = None
                    for element in elements:
                        tmp = element
                        tagname = element.tag_name
                        if(tagname == "input"):
                            attr = element.get_attribute("type")
                            try:
                                if(attr == "date"):
                                    driver.execute_script(f'document.getElementsByClassName(`{name}`).value=`{datetime.datetime.now().strftime("%Y-%m-%d")}`;')
                                elif(attr == "file"):
                                    element.send_keys("/var/www/html/SecurityApp/WebAppScanner/Python/DemoUploadFile/win3.jpg")
                                elif(attr == "hidden"):
                                    driver.execute_script(f"document.getElementsByName(`{name}`)[0].setAttribute('value', `{val}`)")
                                else:
                                    element.send_keys(val)
                            except ElementNotInteractableException:
                                continue
                        elif(tagname == "textarea"):
                            element.send_keys(val)
                        elif(tagname == "select"):
                            # ------ option value 変更 ------
                            target_element = element.find_elements_by_css_selector('option')[0]
                            driver.execute_script(f"arguments[0].setAttribute('value',`{val}`)", target_element)
                            list_object = Select(element)
                            list_object.select_by_index(0)
                try:
                    tmp.submit()
                except AttributeError:
                    # HTML内に指定したパラメータが存在しない場合は実行せずにスクショを撮影する
                    pass
    
    # 格納型XSSなど複数アラートが表示される場合があるのですべて削除する
    while(True):
        try:
            Alert(driver).accept()
        except NoAlertPresentException:
            break
    
    # 実行結果のスクショを保存してそのパスを返す
    filepath = DriverScreenShot(CheckAttack)
    return filepath

def CheckSQLi(responsetext, responsehtml_text, CheckAttack, requesturl, requestmotourl, pattern, Method, GETMethodURL):
    for Errortext in SQLINJECTION_ERRORTEXTS:
        search = re.compile(f'.*{Errortext}.*')
        if(Errortext in responsetext):
            for i in responsehtml_text.find_all(text=search):
                result = i.parent
                if(len(str(result)) <= 100):
                    result = result.parent
            
            filepath = ErrorScreenShot(pattern, requestmotourl, CheckAttack, Method, GETMethodURL)
            AddAttackData(CheckAttack, requesturl, requestmotourl, result, pattern, Method, filepath)
            return True


def CheckXSS(responsehtml_text, CheckAttack, requesturl, requestmotourl, pattern, Method, GETMethodURL):
    # 攻撃用のコードにclass="AttackTag"を埋め込みレスポンスのhtmlでクラスとして認識された場合はXSSの脆弱性が存在すると判定する
    AttackTags = responsehtml_text.select(".AttackTag")
    if(len(AttackTags) >= 1):
        filepath = ErrorScreenShot(pattern, requestmotourl, CheckAttack, Method, GETMethodURL)
        AddAttackData(CheckAttack, requesturl, requestmotourl, responsehtml_text, pattern, Method, filepath)
        return True


def HeaderCheck(responseheader, requesturl, requestmotourl,  getcookies, Method):
    # HTTPレスポンスヘッダの分析
    for checkheader in CHECK_RESPONSE_HEADERS:
        if(not (checkheader in responseheader)):
            AddHeaderData(checkheader, requesturl, requestmotourl, responseheader, False, Method)
    if("Set-Cookie" in responseheader):
        for sessidname in sessidnames:
            for check in PHPSESSID_CHECK:
                if(sessidname in responseheader["Set-Cookie"] and not (check in responseheader["Set-Cookie"])):
                    AddHeaderData(check, requesturl, requestmotourl, responseheader, True, Method)
    # ログイン成功時のCookieをチェックする
    for cookie in getcookies:
        for sessidname in sessidnames:
            if("httpOnly" in cookie and cookie["name"] == sessidname):
                if(not cookie["httpOnly"]):
                    AddHeaderData("HttpOnly", requesturl, requestmotourl, responseheader, False, Method)
            if("secure" in cookie and cookie["name"] == sessidname):
                if(not cookie["secure"]):
                    AddHeaderData("Secure", requesturl, requestmotourl, responseheader, False, Method)
            


def VersionCheck(responseheader, CheckAttack, requesturl, requestmotourl, pattern, Method):
    result = ""
    if("Server" in responseheader):
        result = "Server: "+responseheader["Server"]
    if("X-Powered-By" in responseheader):
        result += "\nX-Powered-By: "+responseheader["X-Powered-By"]
    # 正規表現でaddressタグにバージョン情報が存在するかどうかを判定する
    if(re.search(r"[0-9]+\.[0-9]+\.[0-9]+", result)):
        AddAttackData(CheckAttack, requesturl, requestmotourl, result, pattern, Method)


def HTTPCheck(requesturl, CheckAttack, requestmotourl, pattern, Method):
    protocol = urlparse(requesturl).scheme
    if(protocol == "http"):
        AddAttackData(CheckAttack, requesturl, requestmotourl, "", pattern, Method)


def DirLisCheck(CheckAttack, Method):
    global formnum
    URLLIST = []
    # 遷移先URLの数だけループ
    for url2 in nexturls:
        # 遷移先URLのsrc属性とhref属性を全てALLPATHS配列に格納する
        response = session.get(url2)
        SRCPATHS = bs4.BeautifulSoup(response.text, "html.parser").select("[src]")
        HREFPATHS = bs4.BeautifulSoup(response.text, "html.parser").select("[href]")
        ALLPATHS = list(url2)
        for i in SRCPATHS:
            ALLPATHS.append(i.get("src"))
        for i in HREFPATHS:
            ALLPATHS.append(i.get("href"))
        
        
        for path in ALLPATHS:
            # 元のURLとpath変数のパスを結合して一階層上のディレクトリを取得
            joinurl = urljoin(url2, path)
            joinurl = urljoin(joinurl, "./")
            # そのURLが同一オリジンの場合はディレクトリの階層を上げていき、ディレクトリリスティングの脆弱性がないか調べる
            if(joinurl.startswith(ORIGIN)):
                # オリジンと一致するまでディレクトリの階層を上げていく
                while joinurl != ORIGIN+"/":
                    # まだアクセスしていないディレクトリの場合はGETメソッドを送信し、レスポンスのtitleに「Index of オリジンを除いたパス」が表示されていた
                    # 場合はディレクトリリスティングとして判定する
                    if(not (joinurl in URLLIST)):
                        print(joinurl)
                        URLLIST.append(joinurl)
                        try:
                            response = session.get(joinurl, timeout=10)
                        except Timeout:
                            joinurl = urljoin(joinurl, "../")
                            continue
                        title = bs4.BeautifulSoup(response.text, 'html.parser').select("title")
                        FILEPATH = "Index of "+joinurl.replace(ORIGIN, "")
                        for i in title:
                            if(FILEPATH in i.getText()+"/"):
                                filepath = ErrorScreenShot("", joinurl, CheckAttack, Method, joinurl)
                                AddAttackData(CheckAttack, joinurl, joinurl, response.text[:1000]+"\n...", "", Method, filepath)
                                # 攻撃名のキーが重複して上書きしてしまうので詳細情報を格納する配列を増やしてフォーム番号も+1する
                                AddDictData()
                                formnum += 1
                    joinurl = urljoin(joinurl, "../")


def OScommandCheck(responsetext, responsehtml_text, CheckAttack, requesturl, requestmotourl, pattern, Method, GETMethodURL):
    if("uid=" in responsetext and "gid=" in responsetext and "groups=" in responsetext):
        # 特定の文字列を検索してその要素を取得する 参考: https://teratail.com/questions/147524
        search = re.compile('.*uid=.*')
        result = ""
        for i in responsehtml_text.find_all(text=search):
            result = i.parent
        filepath = ErrorScreenShot(pattern, requestmotourl, CheckAttack, Method, GETMethodURL)
        AddAttackData(CheckAttack, requesturl, requestmotourl, result, pattern, Method, filepath)
        return True


def DirtraversalCheck(responsetext, responsehtml_text, CheckAttack, requesturl, requestmotourl, pattern, Method, GETMethodURL):
    Errortext = "root:x:0:0"
    search = re.compile(f'.*{Errortext}.*')
    if(Errortext in responsetext):
        for i in responsehtml_text.find_all(text=search):
            result = i.parent
            if(len(str(result)) <= 100):
                result = result.parent
        filepath = ErrorScreenShot(pattern, requestmotourl, CheckAttack, Method, GETMethodURL)
        AddAttackData(CheckAttack, requesturl, requestmotourl, str(result)[:1000]+"\n...", pattern, Method, filepath)
        return True


def OpenRedirectCheck(Method, client_url, logincheck, json_pattern, GETMethodURL):
    hantei = False
    if(logincheck):
        for pattern in OPEN_REDIRECT:
            driver.get(loginurl)
            parameterdict = {}
            for inputtag in driver.find_elements_by_css_selector("input[type='hidden']"):
                nameattribute = inputtag.get_attribute("name")
                if(nameattribute != None and not nameattribute in loginpara.keys()):
                    parameterdict[nameattribute] = pattern
                    test = unquote(pattern)# 二重でURLエンコードされないようデコードした値をセットする
                    driver.execute_script("document.getElementsByName(`"+nameattribute+"`)[0].setAttribute('value', `"+test+"`)")
            jsonparameter = json.dumps(parameterdict)# 辞書を文字列に変換
            element = None
            for i in loginpara.keys():
                element = driver.find_element_by_name(i)
                element.send_keys(loginpara[i])
            element.submit()
            origin = urlparse(driver.current_url).scheme+"://"+urlparse(driver.current_url).netloc
            if(origin == "http://f6c8d1f91c1f0efd093e1a957f8445b6c08372bfd9e71caf168c55ee37a32647"):
                filepath = ErrorScreenShot(jsonparameter, loginurl, ATTACK_NAME[4], Method, GETMethodURL)
                AddAttackData(ATTACK_NAME[4], loginurl, loginurl, "", jsonparameter, Method, filepath)
                hantei = True
            if(hantei):
                driver.delete_all_cookies()
                break
    else:
        if(str(client_url).startswith("http://f6c8d1f91c1f0efd093e1a957f8445b6c08372bfd9e71caf168c55ee37a32647")):
            filepath = ErrorScreenShot(pattern, loginurl, ATTACK_NAME[4], Method, GETMethodURL)
            AddAttackData(ATTACK_NAME[4], loginurl, loginurl, "", json_pattern, Method, filepath)


def HTTPHeaderInjectionCheck(Method, nowcookies, logincheck, json_pattern):
    global driver
    hantei = False
    if(logincheck):
        for pattern in HTTP_HEADERINJECTION:
            driver.get(loginurl)
            parameterdict = {}
            for inputtag in driver.find_elements_by_css_selector("input[type='hidden']"):
                nameattribute = inputtag.get_attribute("name")
                if(nameattribute != None and not nameattribute in loginpara.keys()):
                    parameterdict[nameattribute] = pattern
                    test = pattern
                    # %0d%0aをデコードした値はjavascriptに直接渡せないので、decodeURIを使いJavaScript側でデコードする
                    driver.execute_script("document.getElementsByName('"+inputtag.get_attribute("name")+"')[0].setAttribute('value', decodeURI('"+test+"'))")
            jsonparameter = json.dumps(parameterdict)# 辞書を文字列に変換
            element = None
            for i in loginpara.keys():
                element = driver.find_element_by_name(i)
                element.send_keys(loginpara[i])
            element.submit()
            cookies = driver.get_cookies()
            for cookie in cookies:
                if("HeaderInjectionCookie" in cookie["name"]):
                    AddAttackData(ATTACK_NAME[5], loginurl, loginurl, "", jsonparameter, Method)
                    hantei = True
            if(hantei):
                driver.delete_all_cookies()
                break
    else:
        for cookie in nowcookies:
            if("HeaderInjectionCookie" in cookie.name):
                AddAttackData(ATTACK_NAME[5], loginurl, loginurl, "", json_pattern, Method)
                # Cookieを削除するためにログインしなおす
                driver, session = Login(driver, session, loginurl, loginpara)

    
def ErrorMessageCheck(responsetext, responsehtml_text, CheckAttack, requesturl, requestmotourl, pattern, Method, GETMethodURL):
    if(not Attack_flag[CheckAttack]):
        for Errortext in ERROR_MESSAGE:
            searchtext = Errortext.replace("<b>", "").replace("</b>", "")
            search = re.compile(f'.*{searchtext}.*')
            if(Errortext in responsetext):
                for i in responsehtml_text.find_all(text=search):
                    result = i.parent
                    if(len(str(result)) <= 100):
                        result = result.parent
                filepath = ErrorScreenShot(pattern, requestmotourl, CheckAttack, Method, GETMethodURL)
                Attack_flag[CheckAttack] = True
                AddAttackData(CheckAttack, requesturl, requestmotourl, result, pattern, Method, filepath)
                return True


def CSRFtokenCheck(CheckAttack, requesturl, requestmotourl, pattern, Method, cookies):
    flag = False
    for csrftoken in csrftokens:
        for cookie in cookies:
            if csrftoken == cookie.name:
                flag = True
        for para in json.loads(pattern).keys():
            if csrftoken == para:
                flag = True
    if not flag:
        AddAttackData(CheckAttack, requesturl, requestmotourl, "", pattern, Method)


def HTTPStatusCodeCheck(CheckAttack, requesturl, requestmotourl, pattern, Method, status_code):
    if(not Attack_flag[CheckAttack] and status_code == 500):
        Attack_flag[CheckAttack] = True
        AddAttackData(CheckAttack, requesturl, requestmotourl, "", pattern, Method)
        return True


# レスポンスを分析し、脆弱性が存在するかを判定する関数
def ResponseCheck(CheckAttack, response, pattern, requesturl, requestmotourl, Method, headercheck, cookies, GETMethodURL=""):
    global Errorcounts
    global AttackParameters
    
    responsetext = ""
    responseheader = ""
    client_url = ""
    status_code = ""
    if(isinstance(response, Response)):
        responsetext = response.text
        responseheader = response.headers
        client_url = response.url
        status_code = response.status_code
    
    if(isinstance(response, dict)):
        responseheader = response
    
    responsehtml_text = bs4.BeautifulSoup(responsetext, 'html.parser')
    
    # 不要なエラーメッセージに対する判定はすべてのリクエストに対して行う
    ErrorMessageCheck(responsetext, responsehtml_text, ATTACK_NAME[10], requesturl, requestmotourl, pattern, Method, GETMethodURL)
    HTTPStatusCodeCheck(ATTACK_NAME[12], requesturl, requestmotourl, pattern, Method, status_code)
    
    
    # SQLインジェクションの判定
    if(CheckAttack == ATTACK_NAME[0]):
        return CheckSQLi(responsetext, responsehtml_text, CheckAttack, requesturl, requestmotourl, pattern, Method, GETMethodURL)
    
    # XSSの判定
    if(CheckAttack == ATTACK_NAME[1]):
        return CheckXSS(responsehtml_text, CheckAttack, requesturl, requestmotourl, pattern, Method, GETMethodURL)

    # HTTPレスポンスヘッダのチェック
    if(headercheck):
        HeaderCheck(responseheader, requesturl, requestmotourl, cookies, Method)
    
    # バージョン情報漏洩の確認
    if(CheckAttack == ATTACK_NAME[7]):
        VersionCheck(responseheader, CheckAttack, requesturl, requestmotourl, pattern, Method)
    
    # 当該ページがHTTPS通信かどうかを確認する
    if(CheckAttack == ATTACK_NAME[8]):
        HTTPCheck(requesturl, CheckAttack, requestmotourl, pattern, Method)
    
    # ディレクトリリスティングの確認
    if(CheckAttack == ATTACK_NAME[9]):
        DirLisCheck(CheckAttack, Method)
    
    # オープンリダイレクトの判定
    if(CheckAttack == ATTACK_NAME[4]):
        OpenRedirectCheck(Method, client_url, False, pattern, GETMethodURL)
    
    # HTTPヘッダインジェクションの判定
    if(CheckAttack == ATTACK_NAME[5]):
        HTTPHeaderInjectionCheck(Method, cookies, False, pattern)
    
    # OSコマンドインジェクションの判定(Linuxサーバにしか対応していないので、Ubuntuを起動して「sudo php -S IPアドレス:80 -t .」でLinuxサーバを起動する必要がある)
    if(CheckAttack == ATTACK_NAME[2]):
        return OScommandCheck(responsetext, responsehtml_text, CheckAttack, requesturl, requestmotourl, pattern, Method, GETMethodURL)
    
    # ディレクトリトラバーサルの判定
    if(CheckAttack == ATTACK_NAME[3]):
        return DirtraversalCheck(responsetext, responsehtml_text, CheckAttack, requesturl, requestmotourl, pattern, Method, GETMethodURL)
    
    return False


# そのページのパラメータを取得する関数
def GetParameters(forms, formnexturls, formmethods, parameters, UniqueValues, loopurl):
    # フォームごとの遷移先URL・メソッド・パラメータを取得する
    for i in forms:
        if("action" not in i.attrs):
            i.attrs["action"] = ""
        if("method" not in i.attrs):
            i.attrs["method"] = "get"
        if(i.attrs["action"] == ""):
            nexturl = loopurl
        nexturl = urljoin(loopurl, i.attrs["action"])
        method = i.attrs["method"]
        inputs = i.select("input")
        textareas = i.select("textarea")
        selects = i.select("select")
        parameter = {}
        for j in inputs:
            # type属性がなくてname属性があるパラメータはテキストとして追加しておく
            if(not ("type" in j.attrs.keys()) and ("name" in j.attrs.keys())):
                parameter[j.attrs["name"]] =  ""
            else:
                if(j.attrs["type"] == "text" or j.attrs["type"] == "password" or j.attrs["type"] == "search"):
                    if("name" in j.attrs.keys()):
                        parameter[j.attrs["name"]] =  ""
                elif("name" in j.attrs.keys()):
                    if(j.attrs["type"] == "file"):
                        # type属性がfileの場合はjpegの画像ファイルをアップロードする 参考: https://blog.hikaru.run/2023/02/05/send-multipart-files-using-requests.html
                        UniqueValues[j.attrs["name"]] = {j.attrs["name"]: ('test.jpg', open('./Python/DemoUploadFile/win3.jpg', 'rb'), 'image/jpeg')}
                        parameter[j.attrs["name"]] = {j.attrs["name"]: ('test.jpg', open('./Python/DemoUploadFile/win3.jpg', 'rb'), 'image/jpeg')}
                    elif(j.attrs["type"] == "date"):
                        # type属性がdateの場合は現在の日付を使用する
                        UniqueValues[j.attrs["name"]] = datetime.datetime.now().strftime("%Y-%m-%d")
                        parameter[j.attrs["name"]] = datetime.datetime.now().strftime("%Y-%m-%d")
                    # 入力欄以外はvalueの値をそのまま使う
                    elif("value" in j.attrs.keys()):
                        UniqueValues[j.attrs["name"]] = j.attrs['value']
                        parameter[j.attrs["name"]] = j.attrs['value']
                    else:
                        # それ以外の場合は空にしておく(後から文字列「demodata」を挿入する)
                        parameter[j.attrs["name"]] =  ""
            # name属性またはtype属性がよく使われるもので入力制限がある場合はそれ用のテストデータをセットする
            if("name" in j.attrs):
                if(j.attrs["name"] in KEYVALUES and j.attrs["name"] not in UniqueValues):
                    UniqueValues[j.attrs["name"]] = KEYVALUES[j.attrs["name"]]
                    parameter[j.attrs["name"]] = KEYVALUES[j.attrs["name"]]
                if("type" in j.attrs):
                    if(j.attrs["type"] in KEYVALUES and j.attrs["name"] not in UniqueValues):
                        UniqueValues[j.attrs["name"]] = KEYVALUES[j.attrs["type"]]
                        parameter[j.attrs["name"]] = KEYVALUES[j.attrs["type"]]
                            
        for j in textareas:
            parameter[j.attrs["name"]] =  ""
        for j in selects:
            # selectの場合は一番最初の選択肢を使用する
            options = j.select("option")
            UniqueValues[j.attrs["name"]] = options[0].attrs["value"]
            parameter[j.attrs["name"]] = options[0].attrs["value"]
        
        
        formnexturls.append(nexturl)
        formmethods.append(method)
        parameters.append(parameter)
    
    return formnexturls, formmethods, parameters, UniqueValues


# 指定されたページに対してのリクエスト数を計算する関数
def GetReqCnt(nexturls, session, BLACK_LIST):
    blacklistlen = 0
    SumCodeCnt = 0
    for item in BLACK_LIST:
        blacklistlen += len(item)
    
    
    # フォームの数だけ増やす
    for nexturl in nexturls:
        res = session.get(nexturl)
        html_text = bs4.BeautifulSoup(res.text, 'html.parser')
        forms = html_text.select("form")
        paracnt = 0
        # フォームごとの遷移先URL・メソッド・パラメータを取得する
        for i in forms:
            inputs = i.select("input")
            textareas = i.select("textarea")
            selects = i.select("select")
            for j in inputs:
                if(not ("type" in j.attrs.keys()) and ("name" in j.attrs.keys())):
                    paracnt += 1
                else:
                    if(j.attrs["type"] == "text" or j.attrs["type"] == "password" or j.attrs["type"] == "search"):
                        paracnt += 1
                    elif("name" in j.attrs.keys()):
                        paracnt += 1
            for j in textareas:
                paracnt += 1
            for j in selects:
                paracnt += 1
        # getパラメータも調べる
        getpara = parse_qs(urlparse(nexturl).query)
        if(len(getpara) >= 1):
            SumCodeCnt += blacklistlen * len(getpara)
        SumCodeCnt += blacklistlen * paracnt
    return SumCodeCnt

# DOM-based-XSSかどうかを判定するための関数
def CheckXSSType(driver, xsspattern, jsonparameter):
    domresult = ""
    imgpath = ""
    domsuccess = False
    while(True):
        try:
            titletext = Alert(driver).text
            Alert(driver).accept()
            # アラートが鳴っていた場合そのダイアログの文字列を取得し、「1」でかつ検査パターンがAngular用の値だった場合は反射型のXSSとして判定する
            if(xsspattern in ANGULARPATTER and titletext == "1"):
                AddAttackData(ATTACK_NAME[1], loopurl, loopurl, "", jsonparameter, "", "")
        except NoAlertPresentException:
            break
    # 反射型・格納型XSSはページを更新してもXSSの要素が残る仕組みになっているのでそれを利用してDOM-based-XSSを判定する
    SearchAttackTag = len(driver.find_elements_by_css_selector(".AttackTag"))
    if(SearchAttackTag >= 1):
        try:
            # 要素が埋め込まれている状態のソースコードを保存しておく
            domresult = driver.page_source
            imgpath = DriverScreenShot(ATTACK_NAME[6])
            # ページを更新してDOM-based-XSSかどうかを調べる
            driver.refresh()
            SearchAttackTag = len(driver.find_elements_by_css_selector(".AttackTag"))
            # ページを更新したときにAttackTagが無くなった場合はDOM-based-XSSとして判定する
            if(SearchAttackTag <= 0):
                domsuccess = True
        except UnexpectedAlertPresentException:
            # ページを更新したときにアラートが発生した場合は反射型・格納型XSSである可能性が高いので、domsuccessをFalseにする
            domsuccess = False
    if(not domsuccess):
        # DOM-based-XSSじゃなかった場合は証拠となるソースコードとスクショを空文字にする
        domresult = ""
        imgpath = ""
    return driver, domsuccess, domresult, imgpath
    
    
# DOM Based XSSを検査するための関数
def DOMBasedXSSCheck(driver, loopurl, NowCnt, SumCodeCnt, alertcnt, percent):
    domsuccess = False
    nameattr = ""
    hitpattern = ""
    domresult = ""
    imgpath = ""
    for xsspattern in XSS:
        try:
            driver.get(loopurl)
            cnt = len(driver.find_elements_by_css_selector("input[type='text'], input[type='search'], input[type='email'], input[type='url'], input[type='password'], textarea"))
            for i in range(cnt):
                # 各入力欄に対してXSSペイロードを入力・実行し、DOM-based-XSSを調べていく
                driver.get(loopurl)
                elements = driver.find_elements_by_css_selector("input[type='text'], input[type='search'], input[type='email'], input[type='url'], input[type='password'], textarea")
                nameattr = elements[i].get_attribute("name")
                # 大まかな現在の進捗状況をDBに保存する
                jsonparameter = json.dumps({nameattr: xsspattern})
                SaveDB("診断中", loopurl, jsonparameter, NowCnt, SumCodeCnt, percent, alertcnt, "")
                hitpattern = xsspattern
                elements[i].send_keys(xsspattern)
                try:
                    # DOM-based-XSSでもsubmit操作をしないと実行しない物もあるのでsubmitする
                    elements[i].submit()
                except NoSuchElementException:
                    # submit機能がない要素だった場合はpassする
                    pass
                # XSSの種類を判定し、DOM-based-XSSだった場合は処理を抜ける
                driver, domsuccess, domresult, imgpath = CheckXSSType(driver, xsspattern, jsonparameter)
                if(domsuccess or i > 10):
                    break
            # 「#」を使ったXSSも検査する
            driver.get(loopurl + "#" + xsspattern)
            # 大まかな現在の進捗状況をDBに保存する
            jsonparameter = json.dumps({"#": xsspattern})
            SaveDB("診断中", loopurl, jsonparameter, NowCnt, SumCodeCnt, percent, alertcnt, "")
            Alert(driver).accept()
        except UnexpectedAlertPresentException:
            # AttackTagが埋め込まれているかを判定する
            driver, domsuccess, domresult, imgpath = CheckXSSType(driver, xsspattern, jsonparameter)
        except NoAlertPresentException:
            pass
        except IndexError:
            pass
        except ElementNotInteractableException:
            pass
        
        # 格納型XSSなど複数アラートが表示される場合があるのですべて削除する
        while(True):
            try:
                Alert(driver).accept()
            except NoAlertPresentException:
                break
        # DOM-based-XSSが検出された場合はこれ以上検査しない
        if(domsuccess):
            break
    if(nameattr == None):
        nameattr = ""
    # DOM-based-XSSの脆弱性が検出された場合はその情報を連想配列に追加する
    if(domsuccess):
        jsonparameter = json.dumps({nameattr: hitpattern})
        AddAttackData(ATTACK_NAME[6], loopurl, loopurl, domresult, jsonparameter, "", imgpath)


# パラメータに値をセットする関数
def ParaSetVal(parameters2, pattern, UniqueValues2, csrftokens, session, loopurl, nowform, FileFlag2, FileData2, FileKey2, attackparameter):
    # フォームに試験値をセットする
    for key in parameters2[nowform].keys():
        # パラメータ内に一つでもtype=fileがある場合はFileFlagをTrueにする
        if(isinstance(parameters2[nowform][key], dict)):
            FileFlag2 = True
            FileData2 =  parameters2[nowform][key]
            FileKey2 = key
        if(key == attackparameter):
            # フォーム一つ一つに対して順番に試験値をセットする
            parameters2[nowform][key] = pattern
        elif(key in UniqueValues2.keys()):
            # hiddenやselectに対しては初期値を使用
            parameters2[nowform][key] = UniqueValues2[key]
            if(key in csrftokens):
                # CSRFトークンの場合は最新のCSRFトークンをセットする
                responsehtml_text = bs4.BeautifulSoup(session.get(loopurl).text, 'html.parser')
                parameters2[nowform][key] = responsehtml_text.select(f"input[name='{key}']")[0].get("value")
            # input属性がfileの場合はfileデータ送信用の変数にデータを格納する
            if(isinstance(parameters2[nowform][key], dict)):
                FileFlag2 = True
                FileData2 =  parameters2[nowform][key]
                FileKey2 = key
        else:
            # それ以外の入力値はdemodata文字列を挿入する
            parameters2[nowform][key] = "demodata"
            
    return parameters2, UniqueValues2, session, FileFlag2, FileData2, FileKey2


# 試験値をセットしたリクエストを送信して脆弱性を検査する関数
def AttackRequest(formmethods, formnexturls, Attack_flag, syuruiindex, FileFlag, FileKey, FileData, parameters, session, csrftokens, loopurl, jsonparameter, pattern, nowform):
    if(formmethods[nowform].lower() == "post"):
        if(not Attack_flag[ATTACK_NAME[syuruiindex]]):
            try:
                if(FileFlag):
                    # inputデータの中にfile属性がある場合はmultipart/form-data形式で送信する
                    tmpparameters = parameters[nowform].copy()
                    tmpparameters.pop(FileKey)
                    response = session.post(formnexturls[nowform], data=tmpparameters, timeout=3, files=FileData)
                else:
                    response = session.post(formnexturls[nowform], data=parameters[nowform], timeout=3)
                # CSRFトークンが設定されている場合は、トークンの有無をチェックする
                if(len(csrftokens) > 0):
                    CSRFtokenCheck(ATTACK_NAME[11], formnexturls[nowform], loopurl, jsonparameter, "POST", session.cookies)
                success = ResponseCheck(ATTACK_NAME[syuruiindex], response, jsonparameter, formnexturls[nowform], loopurl, "POST", False, session.cookies)
            except Timeout:
                # Timeoutを使用して、ブラインドSQLインジェクションとブラインドOSコマンドインジェクションの判定を行う
                if((ATTACK_NAME[syuruiindex] == "SQLインジェクション攻撃" or ATTACK_NAME[syuruiindex] == "OSコマンドインジェクション") and "sleep" in pattern):
                    AddAttackData(ATTACK_NAME[syuruiindex], formnexturls[nowform], loopurl, "", jsonparameter, "post")
                    success = True
            except RemoteDisconnected:
                success = False
                print("error!!")
            except LocationParseError:
                success = False
                print("error!!")
            except ConnectionError:
                success = False
                print("error!!")
        else:
            # すでに検出済みの場合は他にパラメータもスキップする
            success = True
        
        # 段階を踏むページだった場合は立て続けにリクエストを送信する
        if(not success):
            if(loopurl in StepActions):
                if(response.url in StepActions[loopurl]):
                    newurl = response.url
                    formnexturls2 = []
                    formmethods2 = []
                    parameters2 = []
                    UniqueValues2 = {}
                    html_text2 = bs4.BeautifulSoup(response.text, 'html.parser')
                    forms2 = html_text2.select("form")
                    # フォームごとの遷移先URL・メソッド・パラメータを取得する
                    formnexturls2, formmethods2, parameters2, UniqueValues2 = GetParameters(forms2, formnexturls2, formmethods2, parameters2, UniqueValues2, newurl)
                    for nowform2 in range(0, len(formnexturls2)):
                        # パラメータに値をセットする
                        parameters2, UniqueValues2, session, FileFlag2, FileData2, FileKey2 = ParaSetVal(parameters2, pattern, UniqueValues2, csrftokens, session, newurl, nowform2, FileFlag, FileData, FileKey, attackparameter)
                        # さらにリクエストを送信して脆弱性を検査する
                        success, session = AttackRequest(formmethods2, formnexturls2, Attack_flag, syuruiindex, FileFlag2, FileKey2, FileData2, parameters2, session, csrftokens, newurl, jsonparameter, pattern, nowform2)
            
    elif(formmethods[nowform].lower() == "get"):
        if(not Attack_flag[ATTACK_NAME[syuruiindex]]):
            geturl = formnexturls[nowform]+"?"
            for getpara in parameters[nowform].keys():
                val = parameters[nowform][getpara]
                geturl += getpara+"="+val+"&"
            geturl = str(geturl[:len(geturl)-1]).replace("\n", "")
            
            try:
                response = session.get(geturl, timeout=3)
                success = ResponseCheck(ATTACK_NAME[syuruiindex], response, jsonparameter, formnexturls[nowform], formnexturls[nowform], "GET", False, session.cookies, geturl)
            except Timeout:
                # Timeoutを使用して、ブラインドSQLインジェクションとブラインドOSコマンドインジェクションの判定を行う
                if((ATTACK_NAME[syuruiindex] == "SQLインジェクション攻撃" or ATTACK_NAME[syuruiindex] == "OSコマンドインジェクション") and "sleep" in pattern):
                    AddAttackData(ATTACK_NAME[syuruiindex], formnexturls[nowform], loopurl, "", jsonparameter, "get")
                    success = True
        else:
            success = True

    return success, session


# getパラメータに試験値をセットしたURLを生成する関数
def SetGetParameter(url, parameters):
    geturl = url.split('?')[0] + "?"
    for getpara in parameters.keys():
        if(type(parameters[getpara]) is list):
            val = parameters[getpara][0]
        else:
            val = parameters[getpara]
        geturl += getpara+"="+val+"&"
    geturl = str(geturl[:len(geturl)-1]).replace("\n", "")
    return geturl


# 高度な巡回による診断の場合はあらかじめ保存されたリクエストに試験値をセットして診断する
def AdvancedAttackRequest(nexturls, advanced_urls, AllURLCnt, alertcnt):
    SumCodeCnt = 0
    NowCnt = 0
    percent = "0.0%"
    
    reqitem = advanced_urls["requests"].pop(0)
    # すでに検出済みの攻撃をスキップするためのフラグをリセットする
    for attackname in ATTACK_NAME:
        Attack_flag[attackname] = False
    
    
    for url in reqitem.keys():
        SumCodeCnt = 0
        NowCnt = 0
        parameters = json.loads(reqitem[url]["params"])

        for attackpara in BLACK_LIST:
            SumCodeCnt += len(attackpara)
        
        SumCodeCnt = SumCodeCnt * len(parameters.keys())
            
        
        for para in parameters.keys():
            for syuruiindex, attackcodes in enumerate(BLACK_LIST, 0):
                # 現在のテスト済み試験値数を格納する変数
                checkpatterncnt = 0
                for pattern in attackcodes:
                    success = False
                    checkpatterncnt += 1
                    method = reqitem[url]["method"]
                    response = None
                    headers = json.loads(reqitem[url]["headers"])
                    success = False
                    
                    tmpparameters = parameters.copy()
                    # 試験値をセット
                    for key in tmpparameters.keys():
                        if(key == para):
                            tmpparameters[para] = pattern
                        else:
                            if(type(tmpparameters[key]) is list):
                                tmpparameters[key] = tmpparameters[key][0]
                            else:
                                tmpparameters[key] = tmpparameters[key]
                    
                    jsonparameter = json.dumps(tmpparameters)
                    
                    try:
                        if(method == "post"):
                            try:
                                response = session.post(url, data=tmpparameters, headers=headers, timeout=3)
                                success = ResponseCheck(ATTACK_NAME[syuruiindex], response, jsonparameter, url, url, method, False, session.cookies)
                            except LocationParseError:
                                success = False
                                pass
                        elif(method == "get"):
                            geturl = SetGetParameter(url, tmpparameters)
                            response = session.get(geturl, timeout=3)
                            success = ResponseCheck(ATTACK_NAME[syuruiindex], response, jsonparameter, url, url, method, False, session.cookies, geturl)
                    except Timeout:
                        # Timeoutを使用して、ブラインドSQLインジェクションとブラインドOSコマンドインジェクションの判定を行う
                        if((ATTACK_NAME[syuruiindex] == "SQLインジェクション攻撃" or ATTACK_NAME[syuruiindex] == "OSコマンドインジェクション") and "sleep" in pattern):
                            AddAttackData(ATTACK_NAME[syuruiindex], url, url, "", jsonparameter, "post")
                            success = True
                    
                    # 脆弱性を検出した場合は残りの試験値を加算して次の検査項目へ移る
                    if(success):
                        NowCnt += len(attackcodes) - checkpatterncnt+1
                        Attack_flag[ATTACK_NAME[syuruiindex]] = True
                    else:
                        NowCnt += 1
                    # 各攻撃コードごとの結果をDBに保存する
                    percent = str(round((NowCnt/SumCodeCnt)*100, 1))+"%"
                    alertcnt = GetAllCnt(Errorcounts, HeaderAlertCount)
                    jsonparameter = json.dumps(tmpparameters)
                    SaveDB("診断中", url, jsonparameter, NowCnt, SumCodeCnt, percent, alertcnt, "", AllURLCnt, AllURLCnt - len(nexturls))
                    # 脆弱性を検出した場合は次の検査項目へ移る
                    if(success):
                        break
                    
                    # ページが更新されたり閉じたりしたら強制終了する
                    haitacheck = requests.post("http://127.0.0.1/SecurityApp/WebAppScanner/HaitaCheck.php", {"check": "yes"})
                    if(haitacheck.text == "NotReady"):
                        # NotReadyをReadyに戻してDBをリセットして強制終了
                        requests.post("http://127.0.0.1/SecurityApp/WebAppScanner/HaitaCheck.php", {"check": "no"})
                        AttackInfoReset()
                        driver.quit()
                        exit(0)
    
    return alertcnt  



# 攻撃のパターンとそれに対応した攻撃名
SQLINJECTION = []
XSS = []
OSCOMMAND = []
DIR_TRAVERSAL = []
OPEN_REDIRECT = []
HTTP_HEADERINJECTION = []

SetPattern()# パターンの初期化
    
BLACK_LIST = [SQLINJECTION, XSS, OSCOMMAND, DIR_TRAVERSAL, OPEN_REDIRECT, HTTP_HEADERINJECTION] # サイトごとに大量のリクエストを送る必要のない攻撃は追加しない
ATTACK_NAME = ["SQLインジェクション攻撃", "XSS", "OSコマンドインジェクション", "ディレクトリトラバーサル",
               "オープンリダイレクト","HTTPヘッダインジェクション", "DOM Based XSS", "バージョン情報の漏洩", "HTTPによる通信",
               "ディレクトリリスティング", "不要なエラーメッセージ", "CSRFトークンの有無", "HTTPステータスコード500-内部エラー"]
Attack_flag = {}
for attackname in ATTACK_NAME:
    Attack_flag[attackname] = False

SaveDB("ドライバの設定中", "", "", 0, 0, "0.0%", 0, "")

# chromedriverの設定

options = Options()
options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
# ウィンドウサイズを最大化する
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
sql = "SELECT manualurls_json, loginpara_json, loginurl, method, sessids_json, csrftokens_json, loginflagstr, loginflagpage FROM scannersetting"
cur.execute(sql)

# 実行結果を取得する
rows = cur.fetchall()

manualurls = []
loginpara = dict()
loginurl = ""
loginmethod = ""
sessidnames = []
csrftokens = []
loginflagstr = ""
loginflagpage = ""
# 1行ずつ表示する
for row in rows:
    manualurls = json.loads(row[0])
    loginpara = json.loads(row[1])
    loginurl = row[2]
    loginmethod = str(row[3]).upper()
    sessidnames = json.loads(row[4])
    csrftokens = json.loads(row[5])
    loginflagstr = row[6]
    loginflagpage = row[7]

# scanidの最大値を取得し、+1することで現在のscanidを取得する
sql2 = "SELECT MAX(scanid) as maxid FROM scandata"
cur.execute(sql2)

# 実行結果を取得する
rows2 = cur.fetchall()
SCANID = None
for row in rows2:
    if(row[0] == None):
        SCANID = 1
        break
    SCANID = int(row[0])+1


# Advancedの設定情報を取得する
sql3 = "SELECT * FROM advanced"
cur.execute(sql3)

# 実行結果を取得する
rows3 = cur.fetchall()
for row in rows3:
    advanced_urls = json.loads(row[2])


cur.close
conn.close


args = sys.argv # コマンドライン引数
# 参考: https://www.slideshare.net/yuichihattori1/python-76928064
# 参考: https://office54.net/python/scraping/beautifulsoup4-html
url = args[1]
ADVANCEDMODE = args[3]

if(ADVANCEDMODE != "yes"):
    # 異なるオリジンに攻撃しないようオリジン名を保存しておく 参考: https://programmer-life.work/python/python-url-to-domain
    ORIGIN = urlparse(url).scheme+"://"+urlparse(url).netloc
    nexturls = [url]

# 手動追加されたURLを配列に追加する
for manualurl in manualurls:
    if(manualurl in nexturls):
        continue
    else:
        nexturls.append(manualurl)

session = requests.session()
driver, session = Login(driver, session, loginurl, loginpara)

AUTOMATICPATROL = args[2]


# 高度な巡回がオンの場合はあらかじめ巡回されたURLをnexturlsに格納する
if(ADVANCEDMODE == "yes"):
    nexturls = []
    tmporigin = None
    for tmp in advanced_urls["requests"]:
        for url in tmp.keys():
            nexturls.append(url)
            tmporigin = url
    ORIGIN = urlparse(tmporigin).scheme+"://"+urlparse(tmporigin).netloc


# 画面遷移用の連想配列の定義
associative_array = {url.replace(ORIGIN, ""): []}
# 画面遷移図PDFファイルのパスを保存する変数
PDFFILEPATH = ""

# 段階を踏んでアクセスするURLを保存する変数
StepActions = {}

if(AUTOMATICPATROL == "yes" and ADVANCEDMODE == "no"):
    SaveDB("巡回中", "", "", 0, 0, "0.0%", 0, "")
    # 画面遷移図用のスクショを保存する連想配列
    pdfimages = {}
    # 巡回結果表示画面で使用する各画面のタイトルを保存する連想配列
    screentitle = {}
    
    # 一番最初のページはスクショはクローラ側でスクショを撮影しないのでこちらで撮影する
    driver.get(url)
    pdfimages, screentitle = ScreenShot(SCANID, driver, pdfimages, url, screentitle)
    
    # nexturls変数にurl変数から遷移可能な全てのURLをnexturlsの配列に格納して、画面遷移図用の連想配列をassociative_arrayに格納する
    nexturls, associative_array, pdfimages, screentitle, StepActions = addnexturl(url, nexturls, ORIGIN, driver, loginurl, loginpara, datetime.datetime.now(), associative_array, pdfimages, SCANID, True, loginflagstr=loginflagstr, loginflagpage=loginflagpage, ScreenTitle=screentitle)
    
    
    # 連想配列から画面遷移図を作成する
    SaveDB("画面遷移図生成中", "", "", 0, 0, "0.0%", 0, "")
    PDFFILEPATH = create_transition_img(associative_array, ORIGIN, loginurl, loginpara, SCANID, False, pdfimages, url, screentitle)
    
    # robots.txtファイルやsitemap.xmlからもURLを抽出する
    nexturls = GetrobotsAndsitemap(driver, session, ORIGIN, nexturls, associative_array)
else:
    # 手動追加したページについても画面のスクショを保存する(複数の手順を踏んでじゃないとアクセスできないページについては未対応)
    # 巡回結果表示画面で使用する各画面のタイトルとimageのpathを保存する連想配列
    pdfimages = {}
    screentitle = {}
    for nexturl in nexturls:
        driver.get(nexturl)
        pdfimages, screentitle = ScreenShot(SCANID, driver, pdfimages, nexturl, screentitle)
        # クローリング中にログアウトしてしまったかどうかを確認して再度ログインする
        if(loginflagpage != ""):
            driver.get(loginflagpage)
            page_source = driver.page_source
        else:
            page_source = ""
        if(loginurl != "" and loginflagstr not in page_source):
            # クローリング中にログアウトしてしまう場合があるので、再度ログインする
            session = requests.session()
            driver, session = Login(driver, session, loginurl, loginpara)

# クローリング中にログアウトしてしまったかどうかを確認して再度ログインする
if(loginflagpage != ""):
    driver.get(loginflagpage)
    page_source = driver.page_source
else:
    page_source = ""
if(loginurl != "" and loginflagstr not in page_source):
    # クローリング中にログアウトしてしまう場合があるので、再度ログインする
    session = requests.session()
    driver, session = Login(driver, session, loginurl, loginpara)


# 合計のパターン数と試行したパターン数を格納する変数
SumCodeCnt = 0
NowCnt = 0
percent = "0.0%"


# レスポンスがエラーかどうかを判定するための文字列(SQLインジェクション)
SQLINJECTION_ERRORTEXTS = ["SQLSTATE"]
# レスポンスに不要なエラーメッセージが含まれていないか判定する文字列
ERROR_MESSAGE = ["Fatal error", "Syntax error", "Warning", "on line "]
# SESSIONIDに推奨される属性
PHPSESSID_CHECK = ["Secure", "HttpOnly"]
# 推奨されるHTTPレスポンスヘッダ(参考: https://www.templarbit.com/blog/jp/2018/07/24/top-http-security-headers-and-how-to-deploy-them/ )
CHECK_RESPONSE_HEADERS = ["X-Frame-Options", "Content-Security-Policy"]

RISK = {"SQLインジェクション攻撃": "Critical",
            "XSS": "High",
            "DOM Based XSS": "High",
            "Secure": "Medium",
            "HttpOnly": "Low",
            "X-Frame-Options": "Medium",
            "Content-Security-Policy": "Medium",
            "バージョン情報の漏洩": "Info",
            "HTTPによる通信": "Medium",
            "ディレクトリリスティング": "Medium",
            "OSコマンドインジェクション": "Critical",
            "ディレクトリトラバーサル": "High",
            "オープンリダイレクト": "Medium",
            "HTTPヘッダインジェクション": "High",
            "不要なエラーメッセージ": "Info",
            "CSRFトークンの有無": "Medium",
            "HTTPステータスコード500-内部エラー": "Info"}

# 検出した脆弱性のリクエスト先URL・リクエスト元URL・レスポンステキスト・攻撃パラメータ・検出回数を保存するための配列の初期化
requestURLs = []
requestMotoURLs = []
requestMethods = []
responseErrortexts = []
AttackParameters = []
ScreenShot = []
Errorcounts = []

HeaderAlertCount = []
HeaderAlertURLs = []
HeaderAlertMotoURLs = []
HeaderAlertMethods = []
HeaderAlertText = []

# 現在のフォーム(URLだけの場合もカウント)を識別するためのformnum変数とalertcnt変数(検出回数)、AllURLCnt変数(遷移可能なURL数)を格納するための変数を初期化
formnum = 0
alertcnt = 0
AllURLCnt = len(nexturls)

AddDictData()# 脆弱性データを保存するための辞書を配列に追加する

# ログイン成功時のオープンリダイレクトとHTTPヘッダインジェクションをチェックする
if(loginurl != ""):
    SaveDB("ログイン処理中", "", "", 0, 0, "0.0%", 0, json.dumps({"urls": nexturls}))
    driver.delete_all_cookies()
    OpenRedirectCheck(loginmethod, "", True, "", "")
    HTTPHeaderInjectionCheck(loginmethod, "", True, "")

# 再度ログイン処理を行う
session = requests.session()
driver, session = Login(driver, session, loginurl, loginpara)

# ログイン情報が設定されている場合は、成功時のCookieをチェックする
if(loginurl != ""):
    for cookie in driver.get_cookies():
        for sessidname in sessidnames:
            if(cookie["name"] == sessidname):
                responseheader = {"Set-Cookie": cookie["name"]+"="+cookie["value"]+";"}
                ResponseCheck("none", responseheader, "", loginurl, loginurl, loginmethod, True, driver.get_cookies())

SaveDB("ディレクトリ探索中", "", "", 0, 0, "0.0%", 0, "")

# 攻撃パラメータを送る前にディレクトリリスティングをチェックする
# ディレクトリリスティングのチェック
ResponseCheck(ATTACK_NAME[9], "", "", "", "", "GET", False, "")

# ディレクトリリスティングで増やしたformnumを初期化する
formnum = 0

# 最後に探索URLをDBに保存するのでコピーしておく
searchurls = nexturls.copy()

# nexturls配列が空になるまでフォーム取得→攻撃パラメータの送信→レスポンスチェックを繰り返す
SaveDB("診断中", "", "", 0, 0, "0.0%", 0, json.dumps({"urls": nexturls}))

while True:
    if(len(nexturls) <= 0):
        break
    loopurl = nexturls.pop(0)
    
    # 診断中にログアウトしてしまったかどうかを確認して再度ログインする
    if(loginflagpage != ""):
        responsetext = session.get(loginflagpage).text
    else:
        responsetext = ""
    if(loginurl != "" and loginflagstr not in responsetext):
        driver, session = Login(driver, session, loginurl, loginpara)
    
    # 段階を踏んでじゃないとアクセスできないページだった場合は処理をしないようにする(StepActions変数を使ってあらかじめ除外しておく処理を追加予定)
    driver.get(loopurl)
    if(driver.current_url != loopurl and driver.current_url in searchurls):
        continue
    
    response = session.get(loopurl)
    # リダイレクトエラーとセッションの問題を修正する必要がある
    html_text = bs4.BeautifulSoup(driver.page_source, 'html.parser')

    # アクセス時にエラーメッセージが表示されていないかどうかを調べる
    ResponseCheck("", response, "", loopurl, loopurl, "GET", False, "", loopurl)
    
    SaveDB("診断中", loopurl, "", NowCnt, SumCodeCnt, percent, alertcnt, "", AllURLCnt, AllURLCnt - len(nexturls))
    
    # 最初に当該ページにDOM-based-XSSがないかを調べる
    driver = SessionCopyToDriver(session, driver)
    try:
        percent = str(round((NowCnt/SumCodeCnt)*100, 1))+"%"
    except ZeroDivisionError:
        percent = "0.0%"
    DOMBasedXSSCheck(driver, loopurl, NowCnt, SumCodeCnt, alertcnt, percent)
    
    # beautifulsoup4を使い、formタグ内のpostパラメータなどを抽出し、攻撃コードのリストファイルを参照しリクエストを送信して
    # そのレスポンスのhtmlなどの変化から脆弱性を検出する
    
    if(ADVANCEDMODE != "yes"):
        # 対象URLのフォームを取得し、遷移先URL・メソッド・パラメータを取得する
        forms = html_text.select("form")
        formnexturls = []
        formmethods = []
        parameters = []
        UniqueValues = {}
        
        # フォームごとの遷移先URL・メソッド・パラメータを取得する
        formnexturls, formmethods, parameters, UniqueValues = GetParameters(forms, formnexturls, formmethods, parameters, UniqueValues, loopurl)
        
        # getパラメータがある場合は取得して、ループ用配列に追加する
        parameter = {}
        getpara = parse_qs(urlparse(loopurl).query)
        for i in getpara.keys():
            parameter[i] = ""
        if(len(parameter) >= 1):
            formnexturls.append(loopurl.split('?')[0])
            formmethods.append("get")
            parameters.append(parameter)

        print(f"遷移先URL: {formnexturls}\nメソッド: {formmethods}\nパラメータ: {parameters}")
    
    
    # 最初に対象URLのレスポンスヘッダとHTTPS通信の有無をチェックする
    response = session.get(loopurl)# session変数を使うとSet-Cookieなど初回アクセス時のヘッダを検査できないのでrequestsを使う
    ResponseCheck("header", response , "", loopurl, loopurl, "GET", True, "")
    # バージョン情報のレスポンスヘッダがないかも確認する
    ResponseCheck(ATTACK_NAME[7], response, "", loopurl, loopurl, "GET", False, "")
    # HTTPS通信の有無のチェック
    ResponseCheck(ATTACK_NAME[7], response, "", loopurl, loopurl, "GET", False, "")
    
    # AdvancedModeがオンの場合はAdvancedAttackRequest関数に移動する
    if(ADVANCEDMODE == "yes"):
        alertcnt = AdvancedAttackRequest(nexturls, advanced_urls, AllURLCnt, alertcnt)
        formnum += 1 # 次のリクエスト用に辞書を追加してformnumを+1する
        AddDictData()
        continue
    
    # 各攻撃コードごとの結果をDBに保存する
    # SumCodeCntが0(全てのURLにフォームが一つもない)場合は探索URLの数から進捗状況を計算する
    if(SumCodeCnt <= 0):
        percent = str(round((AllURLCnt-len(nexturls)/AllURLCnt)*100, 1))+"%"
    else:
        percent = str(round((NowCnt/SumCodeCnt)*100, 1))+"%"
    alertcnt = GetAllCnt(Errorcounts, HeaderAlertCount)
    SaveDB("診断中", loopurl, "", NowCnt, SumCodeCnt, percent, alertcnt, "", AllURLCnt, AllURLCnt - len(nexturls))
    getpara = parse_qs(urlparse(loopurl).query)
    if(len(forms) <= 0 and len(getpara) <= 0):
        formnum += 1 # フォームがないかつgetパラメータもない場合は値を更新してcontinueする
        AddDictData()
        continue


    # リクエスト開始前にリクエスト数の差異を計算する(REQUEST_TO_PAGE辞書から調べてSumCodeCnt変数を調整する)
    reqcnt = GetReqCnt([loopurl], session, BLACK_LIST)
    SumCodeCnt = reqcnt
    NowCnt = 0

    
    # パラメータに攻撃コードを埋め込みリクエストを送信し、そのレスポンスから脆弱性の存在を分析する
    for nowform in range(0, len(formnexturls)):
        # すでに検出済みの攻撃をスキップするためのフラグをリセットする
        for attackname in ATTACK_NAME:
            Attack_flag[attackname] = False
        
        for attackparameter in parameters[nowform].keys():
            FileFlag = False
            FileData = None
            FileKey = ""
            for syuruiindex, attackcodes in enumerate(BLACK_LIST, 0):
                # 現在のテスト済み試験値数を格納する変数
                checkpatterncnt = 0
                for pattern in attackcodes:
                    success = False
                    checkpatterncnt += 1
                    parameters, UniqueValues, session, FileFlag, FileData, FileKey = ParaSetVal(parameters, pattern, UniqueValues, csrftokens, session, loopurl, nowform, FileFlag, FileData, FileKey, attackparameter)
                    
                    tmpparameter = parameters[nowform].copy()
                    if(FileFlag):
                        tmpparameter[FileKey] = "('test.jpg', <_io.BufferedReader name='./Python/DemoUploadFile/win3.jpg'>, 'image/jpeg')"
                    jsonparameter = json.dumps(tmpparameter)# 辞書を文字列に変換
                    
                    # DOM Based XSSの場合はスキップする
                    if(ATTACK_NAME[syuruiindex] == ATTACK_NAME[6]):
                        break
                        
                    # リクエストを送信して脆弱性を検査する
                    success, session = AttackRequest(formmethods, formnexturls, Attack_flag, syuruiindex, FileFlag, FileKey, FileData, parameters, session, csrftokens, loopurl, jsonparameter, pattern, nowform)
                    
                    
                    # 脆弱性を検出した場合は残りの試験値を加算して次の検査項目へ移る
                    if(success):
                        NowCnt += len(attackcodes) - checkpatterncnt+1
                        Attack_flag[ATTACK_NAME[syuruiindex]] = True
                    else:
                        NowCnt += 1
                    # 各攻撃コードごとの結果をDBに保存する
                    percent = str(round((NowCnt/SumCodeCnt)*100, 1))+"%"
                    alertcnt = GetAllCnt(Errorcounts, HeaderAlertCount)
                    SaveDB("診断中", formnexturls[nowform], jsonparameter, NowCnt, SumCodeCnt, percent, alertcnt, "", AllURLCnt, AllURLCnt - len(nexturls))
                    # 脆弱性を検出した場合は次の検査項目へ移る
                    if(success):
                        break
                    
                    # ページが更新されたり閉じたりしたら強制終了する
                    haitacheck = requests.post("http://127.0.0.1/SecurityApp/WebAppScanner/HaitaCheck.php", {"check": "yes"})
                    if(haitacheck.text == "NotReady"):
                        # NotReadyをReadyに戻してDBをリセットして強制終了
                        requests.post("http://127.0.0.1/SecurityApp/WebAppScanner/HaitaCheck.php", {"check": "no"})
                        AttackInfoReset()
                        driver.quit()
                        exit(0)
        formnum += 1
        AddDictData()# フォームが変わるので新たな辞書を配列に追加する

# 最後にオリジンのHTTPS通信の有無・オリジンのレスポンスヘッダにバージョン情報が記載されていないかを調べる
# オリジンのバージョン情報をチェック
response = session.get(ORIGIN)
ResponseCheck(ATTACK_NAME[7], response, "", ORIGIN, ORIGIN, "GET", False, "")
# HTTPS通信のチェック
ResponseCheck(ATTACK_NAME[8], "", "", ORIGIN, ORIGIN, "GET", False, "")
# 診断の進捗状況を更新する
alertcnt = GetAllCnt(Errorcounts, HeaderAlertCount)

SaveDB("診断中", ORIGIN, "", NowCnt, SumCodeCnt, percent, alertcnt, "", AllURLCnt, AllURLCnt - len(nexturls))

# ループを抜けたら配列に格納した情報をフォームごとまとめてDBに保存する
# スキャン結果をDBに保存するためのリクエスト

# VMのApacheだとリクエストヘッダーがapplication/jsonになってしまいPOSTが受け取れないのでPOSTが受け取れるようContent-Typeを指定する
headers = {'content-type': 'application/x-www-form-urlencoded'}
response = requests.post("http://127.0.0.1/SecurityApp/WebAppScanner/AddScanData.php", data={"scanid": SCANID,
                                                                                                                      "domain": url,
                                                                                                                      "formnum": -1,
                                                                                                                      "searchurls[]": searchurls,
                                                                                                                      "pdffilepath": PDFFILEPATH},
                         headers=headers)
# 検出した脆弱性の種類・リクエスト先URL・パラメータを配列などにまとめてフォームごとDBに保存するリクエストを送る
for byformindex in range(0, len(requestURLs)):
    risks = []
    alertattacks = []
    alertrequestURLs = []
    alertrequestMotoURLs = []
    alertrequestMethods = []
    alertparameters = []
    errortexts = []
    alertimgpath = []
    for attackname in requestURLs[byformindex].keys():
        if(len(requestURLs[byformindex][attackname]) >= 1):
            alertattacks.append(attackname)
            alertrequestURLs.append(requestURLs[byformindex][attackname][0])
            alertrequestMotoURLs.append(requestMotoURLs[byformindex][attackname][0])
            alertrequestMethods.append(requestMethods[byformindex][attackname][0])
            alertparameters.append(AttackParameters[byformindex][attackname][0])
            alertimgpath.append(ScreenShot[byformindex][attackname][0])
            # XSSは問題箇所から前後3行(同じ階層)を抽出 参考: https://senablog.com/python-bs4-search/#
            if(attackname == "XSS" or attackname == "DOM Based XSS"):
                nextelement = bs4.BeautifulSoup(str(responseErrortexts[byformindex][attackname][0]), 'html.parser')
                errortext = ""
                nextelement = nextelement.find(class_="AttackTag")
                if(nextelement == None):
                    # AttackTagがなかった場合はDOM Based XSSとみなしhtml文字列は保存しない
                    errortexts.append("")
                else:
                    for k in range(4):
                        if(nextelement.previous_sibling == None):
                            break
                        nextelement = nextelement.previous_sibling
                    for k in range(7):
                        if(nextelement.next_sibling == None):
                            break
                        errortext += str(nextelement.next_sibling)
                        nextelement = nextelement.next_sibling
                    
                    # 前後の要素を取得できなかった場合は挿入したAttackTag要素をそのままerrotextとして登録する
                    if(errortext == ""):
                        errortext = str(nextelement)
                    errortexts.append(errortext)
            else:
                if(len(str(responseErrortexts[byformindex][attackname][0])) > 1000):
                    errortexts.append(str(responseErrortexts[byformindex][attackname][0])[:1000]+"\n...")
                else:
                    errortexts.append(str(responseErrortexts[byformindex][attackname][0]))
            risks.append(RISK[attackname])
    # スキャン結果をDBに保存するためのリクエスト
    response = requests.post("http://127.0.0.1/SecurityApp/WebAppScanner/AddScanData.php", data={
                                                                                                        "alertattacks[]": alertattacks,
                                                                                                        "requesturls[]": alertrequestURLs,
                                                                                                        "requestmotourls[]": alertrequestMotoURLs,
                                                                                                        "requestmethods[]": alertrequestMethods,
                                                                                                        "attackparameters[]": alertparameters,
                                                                                                        "risks[]": risks,
                                                                                                        "errortexts[]": errortexts,
                                                                                                        "alertimgpath[]": alertimgpath,
                                                                                                        "formnum": byformindex},
                             headers=headers)
    
# 検出した推奨されるCookieの属性やHTTPレスポンスヘッダを配列などにまとめてフォームごとにDBに保存するリクエストを送る
for byformindex in range(0, len(HeaderAlertURLs)):
    risks = []
    headeralertnames = []
    HeaderAlertURLs2 = []
    HeaderAlertMotoURLs2 = []
    HeaderAlertMethods2 = []
    HeaderAlertText2 = []
    for alertname in HeaderAlertURLs[byformindex].keys():
        if(len(HeaderAlertURLs[byformindex][alertname]) >= 1):
            headeralertnames.append(alertname)
            HeaderAlertURLs2.append(HeaderAlertURLs[byformindex][alertname][0])
            HeaderAlertMotoURLs2.append(HeaderAlertMotoURLs[byformindex][alertname][0])
            HeaderAlertMethods2.append(HeaderAlertMethods[byformindex][alertname][0])
            HeaderAlertText2.append(HeaderAlertText[byformindex][alertname][0])
            risks.append(RISK[alertname])
    # スキャン結果をDBに保存するためのリクエスト
    response = requests.post("http://127.0.0.1/SecurityApp/WebAppScanner/AddScanData.php", data={
                                                                                                           "headeralertnames[]": headeralertnames,
                                                                                                           "headeralerturls[]": HeaderAlertURLs2,
                                                                                                           "headeralertmotourls[]": HeaderAlertMotoURLs2,
                                                                                                           "headeralertmethods[]": HeaderAlertMethods2,
                                                                                                           "risks[]": risks,
                                                                                                           "errortexts[]": HeaderAlertText2,
                                                                                                           "formnum": byformindex},
                             headers=headers)


# 最後に巡回結果表示画面に表示する画像とタイトルをDBに保存する処理を行う
# カーソルを取得する
cur = conn.cursor()

for pageurl, path in pdfimages.items():
    sql = "INSERT INTO screendata (id, scanid, pageurl, imgpath, pagetitle, time) VALUES (NULL, %s, %s, %s, %s, NOW())"
    cur.execute(sql, (SCANID, pageurl, path, screentitle[pageurl]))
conn.commit()

cur.close()
conn.close()

print(response.text)

driver.quit()
# 100%の状態で1秒待機させてプログラムの終了と同時にjavascriptの方でスキャン結果画面に遷移させる
sleep(1)
# 全ての処理が終わった後もDBをリセット
AttackInfoReset()