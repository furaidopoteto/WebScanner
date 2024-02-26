import requests

# 全てのアラート回数を取得する関数
def GetAllCnt(Errorcounts, HeaderAlertCount):
    allcnt = 0
    for Errocount in Errorcounts:
        allcnt += sum(x>=1 for x in Errocount.values())
    for HeaderAlert in HeaderAlertCount:
        allcnt += sum(x>=1 for x in HeaderAlert.values())
    return allcnt

# 現在の進捗状況をDBに保存する関数
def SaveDB(infotitle, domain, jsonparameter, nowcnt, sumcnt, percent, alertcnt, json_urls, sum_pages="", now_page_cnt=""):
    requests.post("http://127.0.0.1/SecurityApp/WebAppScanner/UpdateAttackInfo.php", data={"infotitle": infotitle,
                                                                                                                    "domain": domain,
                                                                                                                    "parameter": jsonparameter,
                                                                                                                    "nowcnt": nowcnt,
                                                                                                                    "sumcnt": sumcnt,
                                                                                                                    "percent": percent,
                                                                                                                    "alertcnt": alertcnt,
                                                                                                                    "json_urls": json_urls,
                                                                                                                    "sum_pages": sum_pages,
                                                                                                                    "now_page_cnt": now_page_cnt})

# 進捗状況を保存するDBをリセットする関数
def AttackInfoReset():
    requests.post("http://127.0.0.1/SecurityApp/WebAppScanner/UpdateAttackInfo.php", data={"infotitle": "",
                                                                                                        "domain": "",
                                                                                                        "parameter": "",
                                                                                                        "nowcnt": 0,
                                                                                                        "sumcnt": 0,
                                                                                                        "percent": "0.0%",
                                                                                                        "alertcnt": 0,
                                                                                                        "json_urls": "reset",
                                                                                                        "sum_pages": 0,
                                                                                                        "now_page_cnt": 0})