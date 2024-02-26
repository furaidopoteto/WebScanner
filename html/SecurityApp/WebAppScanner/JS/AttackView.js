'use strict';

const inputurl = document.getElementById("inputurl");
const settingbutton = document.getElementById("setting");
const formbox = document.getElementById("formbox");
const scanviewbox = document.getElementById("scanviewbox");
const attackinfobox = document.getElementById("attackinfobox");
const attackurlinfo = document.getElementById("attackurlinfo");
const infotitle = document.getElementById("infotitle");
const domain = document.getElementById("domain");
const parameter = document.getElementById("parameter");
const loadingimg = document.getElementById("loadingimg");
const percent = document.getElementById("percent");
const alertcnt = document.getElementById("alertcnt");

const viewmanualurl = document.getElementById("viewmanualurl");
const viewloginpara = document.getElementById("viewloginpara");
const viewcsrftokensetting = document.getElementById("viewcsrftokensetting");
const viewsessidsetting = document.getElementById("viewsessidsetting");
let loginparameter = {};
let manualurls = [];
let loginurl = "";
let loginmethod = "";
let loginflagstr = "";
let loginflagpage = "";

let CSRFtokens = [];

let SESSIDNames = [];

let AutoPatrol = "yes";

let AdvancedMode = "no";

// 診断中かどうかを判定するための変数
let modehantei = false;

const methodcolors = {"get": "rgb(113, 255, 168)",
                      "post": "rgb(234, 255, 113)", 
                      "put": "rgb(163, 234, 255)", 
                      "patch": "rgb(253, 188, 255)", 
                      "delete": "rgb(255, 119, 119)",
                      "head": "rgb(71, 255, 133)",
                      "options": "rgb(255, 120, 226)"};

// 設定情報をDBから取得して更新する関数
function getsetting(){
    $.ajax({
        type: "post",
        url: "./GetSetting.php",
        dataType: "json",
        data: {"getdata": "yes"}
    }).done(function(kekka){
        manualurls = JSON.parse(kekka["manualurls_json"]);
        loginparameter = JSON.parse(kekka["loginpara_json"]);
        loginurl = kekka["loginurl"];
        loginmethod = kekka["method"];
        loginflagstr = kekka["loginflagstr"];
        loginflagpage = kekka["loginflagpage"];
        SESSIDNames = JSON.parse(kekka["sessids_json"]);
        CSRFtokens = JSON.parse(kekka["csrftokens_json"]);

        if(manualurls.length > 0){
            viewmanualurl.textContent = "手動追加URL: 設定済み";
        }else{
            viewmanualurl.textContent = "手動追加URL: 未設定";
        }
        if(Object.keys(loginparameter).length > 0){
            viewloginpara.textContent = "ログイン情報: 設定済み";
        }else{
            viewloginpara.textContent = "ログイン情報: 未設定";
        }
        if(CSRFtokens.length > 0){
            viewcsrftokensetting.textContent = "CSRFトークン: 設定済み";
        }else{
            viewcsrftokensetting.textContent = "CSRFトークン: 未設定";
        }
        if(SESSIDNames.length > 0){
            viewsessidsetting.textContent = "セッションCookie名: 設定済み";
        }else{
            viewsessidsetting.textContent = "セッションCookie名: 未設定";
        }
    }).fail(function(kekka){
        console.log("設定情報の取得に失敗しました。");
    })
}

// 設定情報を格納する
getsetting();

// 進捗状況を随時取得するためにsetInterval関数を実行する関数
let timerID = null;
function viewstart(){
    timerID = setInterval(getdata, 10);
}

// Pythonの診断用プログラムが更新しているデータベースの情報を取得し、進捗状況として表示する関数
function getdata(){
    $.ajax({
        type: "post",
        url: "./GetAttackInfo.php",
        dataType: "json",
        data: {"getdata": "yes"}
    }).then(function(kekka){
        while(attackurlinfo.firstChild){
            attackurlinfo.removeChild(attackurlinfo.firstChild)
        }
        infotitle.textContent = kekka["infotitle"];
        if(kekka["infotitle"] == "診断中"){
            infotitle.textContent = kekka["infotitle"] + `(${kekka["now_page_cnt"] - 1}/${kekka["sum_pages"]})`;
        }
        let nowpercent = kekka["percent"];
        
        if(parseFloat(nowpercent.replace("%", "")) > 100.0){
            nowpercent = "0.0%";
        }
        
        domain.textContent = kekka["domain"];
        parameter.textContent = kekka["parameter"];
        percent.textContent = nowpercent;
        loadingimg.style.width = nowpercent;
        alertcnt.textContent = kekka["alertcnt"];
        if(kekka['json_urls'].length >= 1 && kekka['json_urls'] != "reset"){
            attackurlinfo.insertAdjacentHTML("beforeend", `<span class="urllist">巡回URL</span><br>`);
            const urls = JSON.parse(kekka['json_urls']);
            for(let i = 0;i<urls["urls"].length;i++){
                attackurlinfo.insertAdjacentHTML("beforeend", `<span class="urllist">${urls["urls"][i]}</span><br>`);
            }
        }
        // たまにまだ完了してないのに診断完了と表示されてしまう不具合を調べる必要がある
        if(nowpercent == "100.0%" && kekka["sum_pages"] == kekka["now_page_cnt"] - 1){
            infotitle.textContent = "診断完了"
        }else if(nowpercent == "100.0%"){
            percent.textContent = "0.0%"
            loadingimg.style.width = "0.0%"
        }
    }).fail(function(kekka){
        console.log("通信に失敗しました");
    })
}

// 100%になったら進捗状況を取得するプログラムのループを終了させる
function end(){
    modehantei = false;
    clearTimeout(timerID);
    $.ajax({
        type: "post",
        url: "./GetMaxScanID.php",
        dataType: "json",
        data: {"getscanid": "yes"}
    }).then(function(kekka){
        location.href = "./ViewScanData.php?scanid="+kekka['maxscanid'];
    }).fail(function(kekka){
        console.log("最大scanidの取得に失敗しました");
    })
}

// 本当に実行しますか？でOKがクリックされたら入力フォームを削除し、診断中のフォームを表示し診断用プログラムを起動する
function start(){
    modehantei = true;
    formbox.style.display = "none";
    scanviewbox.style.display = "none";
    attackinfobox.style.display = "block";
    attackurlinfo.style.display = "block";
    // 設定項目をDBに保存してから診断用プログラムを起動する
    $.ajax({
        type: "post",
        url: "./SetSetting.php",
        dataType: "json",
        contentType: 'application/json',
        data: {"loginurl": loginurl, "loginparameter": JSON.stringify(loginparameter), "loginmethod": loginmethod, "manualurls": JSON.stringify(manualurls), "csrftokens": JSON.stringify(CSRFtokens), "sessids": JSON.stringify(SESSIDNames), "loginflagstr": loginflagstr, "loginflagpage": loginflagpage}// ajaxで連想配列を送る 参考: https://qiita.com/QUANON/items/dd39be7602f9e7226e8e
    }).done(function(kekka){
        $.ajax({
            type: "post",
            url: "./StartScanner.php",
            dataType: "json",
            data: {"url": inputurl.value, "autopatrol": AutoPatrol, "advancedmode": AdvancedMode}
        }).then(function(kekka){
            console.log(kekka);
            end();
            return; // 診断用プログラム開始時・終了時とでviewstart関数が2回呼び出されてしまうので、return文で終了させる
        }).fail(function(kekka){
            console.log(kekka);
            end();
            return;
        })
    }).fail(function(kekka){
        console.log("設定項目保存失敗");
    })
    viewstart();
}


// SweetAlert2でボップアップをおしゃれにする 参考: https://lmn-blog.com/sweet_alert2/ | https://sweetalert2.github.io/ | https://keizokuma.com/sweetalert-keys-main/
function confirmcheck(){
    // 正規表現でURLの形式を確認する
    let flag = checkurl(inputurl.value);

    if(AdvancedMode == "yes"){
        // AdvancedModeがオンの場合はURLを入力せずに開始させる
        flag = true
    }
    if(flag == false){
        Swal.fire({
        title: 'URLの形式が正しくありません'
        , type: 'info'
        }).then(function(result) {
            
        });
    }else{
        Swal.fire({
        title: '本当に実行しますか？'
        , html : '相手の許可なしに攻撃を行うことは犯罪です。<a target="_blank" href="https://www.soumu.go.jp/main_sosiki/joho_tsusin/security/basic/legal/09.html">https://www.soumu.go.jp/main_sosiki/joho_tsusin/security/basic/legal/09.html</a>'
        , showCancelButton : true
        , cancelButtonText : 'やめる'
        , type: 'warning'
        }).then(function(result) {
            // OKが選択されたら診断を開始する関数を呼び出す
            if(result["value"] == true){
                start();
            }
        });
    }
}

// ページが更新されたり閉じたりされた場合にhaitaデータベースを更新し、Pythonプログラムを強制終了させる
// Ajaxで送ってしまうと送信される前にページが閉じてしまうのでnavigator.sendBeaconを使う 参考: https://tech.basicinc.jp/articles/204
window.addEventListener('unload',function(){
    // 診断中にページの更新や閉じられた場合はhaitaデータベースのstateをNotReadyにしてPythonプログラムを停止させる
    if(modehantei){
        const data = new FormData();
        data.append('state', 'stop');
        navigator.sendBeacon("./HaitaCheck.php", data);
    }
    const data2 = new FormData();
    data2.append("state", "stopbrowser");
    navigator.sendBeacon("./SeleniumOperation.php", data2);
});

// 自動巡回のチェックボックスの状態を取得する処理
$(".toggle").on("click", function(element) {
    let divelement = element.target;
    const flag = divelement.classList.contains("AutoPatrolButton");
    if(flag){
        $(divelement).toggleClass("checked");
        if(AutoPatrol == "yes") {
            divelement.querySelector("input").checked = true
            AutoPatrol = "no";
            $('#onofftitle').text("OFF");
        } else {
            divelement.querySelector("input").checked = false
            AutoPatrol = "yes";
            $('#onofftitle').text("ON");
            // 自動巡回と高度な巡回は同時に行えないのでどちらかを自動的にOFFにする
            if(AdvancedMode == "yes"){
                document.querySelector(".AdvancedButton").click();
            }
        }
    }else{
        $(divelement).toggleClass("checked");
        if(AdvancedMode == "no") {
            divelement.querySelector("input").checked = false
            AdvancedMode = "yes";
            $('#onofftitle2').text("ON");
            // 自動巡回と高度な巡回は同時に行えないのでどちらかを自動的にOFFにする
            if(AutoPatrol == "yes"){
                document.querySelector(".AutoPatrolButton").click();
            }
        } else {
            divelement.querySelector("input").checked = true
            AdvancedMode = "no";
            $('#onofftitle2').text("OFF");
        }
    }

    if(AdvancedMode == "yes"){
        document.getElementById("inputurlbox").style.display = "none"
    }else{
        document.getElementById("inputurlbox").style.display = ""
    }
    
});


// ホーム画面に高度な巡回のチェックボタンを表示させるか判定する関数
function AdvancedCheck(){
    $.ajax({
        type: "post",
        url: "./SeleniumOperation.php",
        dataType: "json",
        data: {"state": "getdata"}
    }).done(function(res){
        // 設定されている情報を取得して画面に表示する
        const datas = res.pop();
        advanced_json_urls = JSON.parse(datas["json_urls"]);
        
        const advancedcheck = document.getElementById("advancedcheck");
        if(advanced_json_urls["requests"].length >= 1){
            advancedcheck.style.display = "block";
        }else{
            advancedcheck.style.display = "none";
        }
    }).fail(function(res){
        console.log("Advanced機能の設定情報の取得に失敗しました");
    });
}

AdvancedCheck();

// 歯車マークがクリックされたときに設定画面を表示する処理
settingbutton.addEventListener("click", function(){
    Swal.fire({
        title: '設定',
        width: 1500,
        html: `<div id="settingbox">
                    <div id="leftbox">
                        <a class="leftitems" id="item1" href="javascript: manualurlsetting()">巡回URLの追加</a>
                        <a class="leftitems" id="item2" href="javascript: loginsetting()">ログイン管理</a>
                        <a class="leftitems" id="item3" href="javascript: sessidnamesetting()">セッション管理</a>
                        <a class="leftitems" id="item4" href="javascript: csrftokensetting()">CSRFトークンの設定</a>
                        <a class="leftitems" id="item5" href="javascript: CreatePDFSetting()">画面遷移図生成</a>
                        <a class="leftitems" id="item6" href="javascript: Advanced()">高度な巡回</a>
                    </div>
                    <div id="rightbox">

                    </div>
                </div>`
        ,confirmButtonText: "適用する",
        showCancelButton: true,
        cancelButtonText: '全ての設定情報をリセットする'
        }).then(function(result) {
            if(result["dismiss"] == "cancel"){
                settingreset();
            }
            addformdata(false);
            if(manualurls.length > 0){
                viewmanualurl.textContent = "手動追加URL: 設定済み";
            }else{
                viewmanualurl.textContent = "手動追加URL: 未設定";
            }
            if(Object.keys(loginparameter).length > 0){
                viewloginpara.textContent = "ログイン情報: 設定済み";
            }else{
                viewloginpara.textContent = "ログイン情報: 未設定";
            }
            if(CSRFtokens.length > 0){
                viewcsrftokensetting.textContent = "CSRFトークン: 設定済み";
            }else{
                viewcsrftokensetting.textContent = "CSRFトークン: 未設定";
            }
            if(SESSIDNames.length > 0){
                viewsessidsetting.textContent = "セッションCookie名: 設定済み";
            }else{
                viewsessidsetting.textContent = "セッションCookie名: 未設定";
            }

            AdvancedCheck();
            stopbrowser();
        });
    manualurlsetting();
})


// 手動でURLを追加する画面を表示する関数
function manualurlsetting(){
    addformdata(true);
    colorchange("item1");
    viewurls();
}

// 手動で入力されたURLを追加する関数
function addmanualurl(){
    const inputaddurl = document.getElementById("inputaddurl");
    if(inputaddurl == null){
        return;
    }
    // 正規表現でURLの形式を確認する
    const flag = checkurl(inputaddurl.value);
    if(flag){
        if(inputaddurl != null && manualurls.indexOf(inputaddurl.value) < 0){
            manualurls.push(inputaddurl.value);
            viewurls()
        }else{
            const settingurlerror = document.getElementById("settingurlerror");
            settingurlerror.textContent = "指定したURLはすでに追加済みです";
        }
    }else{
        const settingurlerror = document.getElementById("settingurlerror");
        settingurlerror.textContent = "URLの形式が正しくありません";
    }
}

// 追加されたURLを表示する関数
function viewurls(){
    const rightbox = removerightbox();
    rightbox.insertAdjacentHTML("afterbegin", `<span class="settingtext">・巡回URL</span>
                                                <input id="inputaddurl" class="settinginput" type="text" name="addurl">
                                                <button style="font-size: 30px;" id="addurlbutton" onclick="javascript: addmanualurl()">追加</button><br>
                                                <button style="font-size: 30px;" id="addjunkaibutton" onclick="javascript: addjunkaiurl()">巡回して追加</button>
                                                <h3 style="color: red;" id="settingurlerror"></h3>
                                                <h3>追加したURL一覧<br>※手動追加したURLから巡回先を探索することはありません</h3>`);
    for(let i = 0;i<manualurls.length;i++){
        rightbox.insertAdjacentHTML("beforeend", `<span class="viewurls">・<label class="viewurlitem">"${manualurls[i]}</label><label class="viewremovebutton"><a href="javascript: delmanualurl('${manualurls[i]}')">取消</a></label></span><br>`);
    }
}

// 指定されたURLを配列から削除する関数
function delmanualurl(url){
    if(url != null && manualurls.indexOf(url) >= 0){
        manualurls.splice(manualurls.indexOf(url), 1);
        viewurls()
    }
}

// 指定されたURLからクローリングして取得したURLを配列に格納する関数
function addjunkaiurl(){
    const inputaddurl = document.getElementById("inputaddurl");
    if(inputaddurl == null){
        return;
    }
    // 正規表現でURLの形式を確認する
    const flag = checkurl(unescape(inputaddurl.value));
    if(flag){
        // 設定項目をDBに保存してから診断用プログラムを起動する
        $.ajax({
            type: "post",
            url: "./SetSetting.php",
            dataType: "json",
            contentType: 'application/json',
            data: {"loginurl": loginurl, "loginparameter": JSON.stringify(loginparameter), "loginmethod": loginmethod, "manualurls": JSON.stringify(manualurls), "csrftokens": JSON.stringify(CSRFtokens), "sessids": JSON.stringify(SESSIDNames), "loginflagstr": loginflagstr, "loginflagpage": loginflagpage}// ajaxで連想配列を送る 参考: https://qiita.com/QUANON/items/dd39be7602f9e7226e8e
        }).done(function(kekka){
            const addjunkaibutton = document.getElementById("addjunkaibutton");
            addjunkaibutton.textContent = "巡回中";
            addjunkaibutton.disabled = true;
            viewloading(true);
            $.ajax({
                type: "post",
                url: "./GetJunkaiURL.php",
                dataType: "json",
                data: {"url": inputaddurl.value, "loginurl": loginurl, "loginparameter": JSON.stringify(loginparameter)}
            }).done(function(kekka){
                addjunkaibutton.textContent = "巡回して追加";
                addjunkaibutton.disabled = false;
                viewloading(false);
                const urls = JSON.parse(kekka['res'][0]);
                manualurls = urls;
                viewurls();
            }).fail(function(kekka){
                console.log("巡回に失敗しました。");
                viewloading(false);
                addjunkaibutton.textContent = "巡回して追加";
                addjunkaibutton.disabled = false;
            })
        }).fail(function(kekka){
            console.log("設定項目保存失敗");
        })
    }else{
        const settingurlerror = document.getElementById("settingurlerror");
        settingurlerror.textContent = "URLの形式が正しくありません";
    }
}


let RealTimeURLsTimerID = null;
// 追加URL巡回時のローディング画像を表示する関数
function viewloading(flag){
    if(flag){
        $("#loadingbg").addClass("popup-bg-cover");
        $("body > div.swal2-container.swal2-center.swal2-shown > div").css("display", "none");
        startRealTimeURLs();
    }else{
        $("#loadingbg").removeClass("popup-bg-cover");
        $("body > div.swal2-container.swal2-center.swal2-shown > div").css("display", "flex");
        clearTimeout(RealTimeURLsTimerID);
    }
}

// 設定画面から巡回を行ったときも探索URLをリアルタイムで表示する用の関数
function startRealTimeURLs(){
    RealTimeURLsTimerID = setInterval(ViewRealTimeURLs, 10)
}

// DBから巡回情報を取得して表示する関数
function ViewRealTimeURLs(){
    $.ajax({
        type: "post",
        url: "./GetAttackInfo.php",
        dataType: "json",
        data: {"getdata": "yes"}
    }).done(function(kekka){
        const junkaiurlbox = document.getElementById("junkaiurlbox");
        while(junkaiurlbox.firstChild){
            junkaiurlbox.removeChild(junkaiurlbox.firstChild);
        }
        const urls = JSON.parse(kekka['json_urls']);
        junkaiurlbox.insertAdjacentHTML("beforeend", `<span class="urllist">探索ページ数: ${urls["urls"].length}</span><br>`);
    }).fail(function(kekka){
        console.log("巡回情報の取得に失敗しました");
    })
}

// ログインの設定画面を表示する関数
function loginsetting(){
    colorchange("item2");
    if(loginparameter.length <= 0){
        loginparameter = {};
    }
    const rightbox = removerightbox();
    rightbox.insertAdjacentHTML("afterbegin", `<span class="settingtext">・ログイン画面のURL</span><br>
                                                <input value="${escape(loginurl)}" id="inputloginurl" class="settinginput" type="text">
                                                <button id="searchparabutton" style="font-size: 25px;" onclick="javascript: loginformcheck()">パラメータを調べる</button><br>
                                                <button id="loginresetbutton" style="font-size: 25px;" onclick="javascript: loginreset()">リセット</button>
                                                <h3 style="color: red;" id="settingurlerror"></h3>
                                                `);

    if(loginurl != ""){
        const settingurlerror = document.getElementById("settingurlerror");
        settingurlerror.style.display = "none";
        let keys = [];
        for(let i in loginparameter){
            keys.push(i);
        }
        for(let i = 0;i<keys.length;i++){
            if(keys[i] == "method"){
                loginmethod = paradata[keys[i]];
                continue;
            }
            rightbox.insertAdjacentHTML("beforeend", `<span class="viewinputlogin">
                                        <br>${escape(keys[i])}: <input class="inputloginpara" type="text" name="${escape(keys[i])}" value="${escape(loginparameter[keys[i]])}">
                                        </span>`);
        }
    }
    rightbox.insertAdjacentHTML("beforeend", `<br><span class="settingtext">・ログイン状態を識別する要素または文字列</span><br>
    <input value="${escape(loginflagstr)}" placeholder="(例)<h3>ログアウト</h3>" id="inputloginflagstr" class="settinginput" type="text">
    <br><span class="settingtext">・ログイン状態を識別するURL</span><br>
    <input value="${escape(loginflagpage)}" placeholder="URL" id="inputloginflagpage" class="settinginput" type="text">`)
    addformdata(true);
}

// ログイン画面のパラメータを取得して、設定画面に表示する関数
function loginformcheck(){
    addformdata(true);
    loginparameter = {};
    const rightbox = removerightbox();
    rightbox.insertAdjacentHTML("afterbegin", `<span class="settingtext">・ログイン画面のURL</span><br>
                                                <input value="${escape(loginurl)}" id="inputloginurl" class="settinginput" type="text">
                                                <button id="searchparabutton" style="font-size: 25px;" onclick="javascript: loginformcheck()">パラメータを調べる</button><br>
                                                <button id="loginresetbutton" style="font-size: 25px;" onclick="javascript: loginreset()">リセット</button>
                                                <h3 style="color: red;" id="settingurlerror"></h3>`);
    // 正規表現でURLの形式を確認する
    const flag = checkurl(unescape(loginurl));
    if(flag){
        document.getElementById("searchparabutton").style.display = "none";
        const settingurlerror = document.getElementById("settingurlerror");
        settingurlerror.style.display = "none";
        $.ajax({
            type: "post",
            url: "./StartGetParameter.php",
            dataType: "json",
            data: {"url": loginurl}
        }).then(function(kekka){
            let paradata = JSON.parse(kekka[0]);
            let keys = [];
            for(let i in paradata){
                keys.push(i);
            }
            for(let i = 0;i<keys.length;i++){
                if(keys[i] == "method"){
                    loginmethod = paradata[keys[i]];
                    continue;
                }
                rightbox.insertAdjacentHTML("beforeend", `<span class="viewinputlogin">
                                            <br>${escape(keys[i])}: <input class="inputloginpara" type="text" name="${escape(keys[i])}">
                                            </span>`);
            }
            rightbox.insertAdjacentHTML("beforeend", `<br><span class="settingtext">・ログイン状態を識別する要素または文字列</span><br>
            <input value="${escape(loginflagstr)}" placeholder="(例)<h3>ログアウト</h3>" id="inputloginflagstr" class="settinginput" type="text">
            <br><span class="settingtext">・ログイン状態を識別するURL</span><br>
            <input value="${escape(loginflagpage)}" placeholder="URL" id="inputloginflagpage" class="settinginput" type="text">`)
        }).fail(function(kekka){
            const rightbox = document.getElementById("rightbox");
            rightbox.insertAdjacentHTML("beforeend", `<h3>フォームの取得に失敗しました。</h3>`);
        })
    }else{
        const settingurlerror = document.getElementById("settingurlerror");
        settingurlerror.textContent = "URLの形式が正しくありません";
    }
}

// ログイン情報をリセットする関数
function loginreset(){
    loginurl = "";
    loginparameter = ""
    loginsetting();
}

// セッションCookieの名前を設定する画面を表示する関数
function sessidnamesetting(){
    colorchange("item3");
    addformdata(true);
    viewsessid();
}

//現在設定済みのセッションCookieの名前を表示する関数
function viewsessid(){
    const rightbox = removerightbox();
    rightbox.insertAdjacentHTML("afterbegin", `<span class="settingtext">・セッションCookie名</span><br>
                                                <input id="inputaddsessid" class="settinginput" type="text" name="addsessid">
                                                <button style="font-size: 30px;" id="addurlbutton" onclick="javascript: addsessid()">追加</button>
                                                <h3 style="color: red;" id="settingsessiderror"></h3>
                                                <h3>追加したセッションCookie名一覧</h3>`);
    for(let i = 0;i<SESSIDNames.length;i++){
        rightbox.insertAdjacentHTML("beforeend", `<span class="viewsessid">・${SESSIDNames[i]}<a href="javascript: delsessid('${SESSIDNames[i]}')">取消</a></span><br>`);
    }
}

//入力されたセッションCookie名を追加する関数
function addsessid(){
    const inputaddsessid = document.getElementById("inputaddsessid");
    if(inputaddsessid == null){
        return;
    }
    if(inputaddsessid != null && SESSIDNames.indexOf(inputaddsessid.value) < 0){
        SESSIDNames.push(inputaddsessid.value);
        viewsessid()
    }else{
        const settingsessiderror = document.getElementById("settingsessiderror");
        settingsessiderror.textContent = "指定したセッションCookie名はすでに追加済みです";
    }
}

//指定されたセッションCookie名を配列から削除する関数
function delsessid(sessid){
    if(sessid != null && SESSIDNames.indexOf(sessid) >= 0){
        SESSIDNames.splice(SESSIDNames.indexOf(sessid), 1);
        viewsessid()
    }
}

//CSRFトークン設定画面を表示する関数
function csrftokensetting(){
    addformdata(true);
    colorchange("item4");
    viewcsrftoken();
}

//現在設定済みのCSRFトークンを表示する関数
function viewcsrftoken(){
    const rightbox = removerightbox();
    rightbox.insertAdjacentHTML("afterbegin", `<span class="settingtext">・CSRFトークン名</span><br>
                                                <input id="inputaddcsrftoken" class="settinginput" type="text" name="addcsrftoken">
                                                <button style="font-size: 30px;" id="addurlbutton" onclick="javascript: addcsrftoken()">追加</button>
                                                <h3 style="color: red;" id="settingtokenerror"></h3>
                                                <h3>追加したCSRFトークン一覧</h3>`);
    for(let i = 0;i<CSRFtokens.length;i++){
        rightbox.insertAdjacentHTML("beforeend", `<span class="viewcsrftokens">・${CSRFtokens[i]}<a href="javascript: delcsrftoken('${CSRFtokens[i]}')">取消</a></span><br>`);
    }
}

// 入力されたCSRFトークンを追加する関数
function addcsrftoken(){
    const inputaddcsrftoken = document.getElementById("inputaddcsrftoken");
    if(inputaddcsrftoken == null){
        return;
    }
    if(inputaddcsrftoken != null && CSRFtokens.indexOf(inputaddcsrftoken.value) < 0){
        CSRFtokens.push(inputaddcsrftoken.value);
        viewcsrftoken()
    }else{
        const settingtokenerror = document.getElementById("settingtokenerror");
        settingtokenerror.textContent = "指定したCSRFトークンはすでに追加済みです";
    }
}

// 指定されたCSRFトークンを配列から削除する関数
function delcsrftoken(token){
    if(token != null && CSRFtokens.indexOf(token) >= 0){
        CSRFtokens.splice(CSRFtokens.indexOf(token), 1);
        viewcsrftoken()
    }
}

// 画面遷移図を生成するための設定画面を表示する関数
function CreatePDFSetting(){
    addformdata(true);
    colorchange("item5");
    viewCreatePDF();
}

function viewCreatePDF(){
    const rightbox = removerightbox();
    rightbox.insertAdjacentHTML("afterbegin", `<span class="settingtext">・巡回開始URL</span><br>
                                                <input id="inputCrawlerurl" class="settinginput" type="text">
                                                <button style="font-size: 25px;" onclick="javascript: CreatePDFZip()">画面遷移図生成</button><br>
                                                <h3 style="color: red;" id="settingurlerror"></h3>`);
}

// 画面遷移図を生成するPythonプログラムを呼び出す関数
function CreatePDFZip(){
    const inputCrawlerurl = document.getElementById("inputCrawlerurl");
    const flag = checkurl(inputCrawlerurl.value);
    if(flag){
        // 設定項目をDBに保存してから診断用プログラムを起動する
        $.ajax({
            type: "post",
            url: "./SetSetting.php",
            dataType: "json",
            contentType: 'application/json',
            data: {"loginurl": loginurl, "loginparameter": JSON.stringify(loginparameter), "loginmethod": loginmethod, "manualurls": JSON.stringify(manualurls), "csrftokens": JSON.stringify(CSRFtokens), "sessids": JSON.stringify(SESSIDNames), "loginflagstr": loginflagstr, "loginflagpage": loginflagpage}// ajaxで連想配列を送る 参考: https://qiita.com/QUANON/items/dd39be7602f9e7226e8e
        }).done(function(kekka){
            viewloading(true);
            $.ajax({
                type: "post",
                url: "./StartCreatePDFFileOnly.php",
                dataType: "json",
                data: {"url": inputCrawlerurl.value}
            }).done(function(kekka2){
                console.log(kekka2);
                viewloading(false)
                const filepath = kekka2['res'][0]
                var anchor = document.createElement('a');
                anchor.download = "画面遷移図";
                anchor.href = filepath;
                anchor.click();
            }).fail(function(XMLHttpRequest, textStatus, errorThrown){
                console.log("XMLHttpRequest : " + XMLHttpRequest.status);
                console.log("textStatus     : " + textStatus);
                console.log("errorThrown    : " + errorThrown.message);
            })
        }).fail(function(kekka){
            console.log("設定項目保存失敗");
        })
    }else{
        const settingurlerror = document.getElementById("settingurlerror");
        settingurlerror.textContent = "URLの形式が正しくありません";
    }
}

// 設定画面の右側の表示をリセットする関数
function removerightbox(){
    const rightbox = document.getElementById("rightbox");
    while(rightbox.firstChild){
        rightbox.removeChild(rightbox.firstChild);
    }
    return rightbox;
}

// URLの形式を判定するための関数
function checkurl(val){
    // 正規表現でURLの形式を確認する
    const pattern = /^https?:\/\/[\w/:%#\$&\?\(\)~\.=\+\-]+$/;
    return pattern.test(val);
}

// 設定のフォームデータを取得する関数
function addformdata(addmanualurlflag){
    if(addmanualurlflag){
        addmanualurl();
    }
    const inputloginpara = document.getElementsByClassName("inputloginpara");
    if(inputloginpara.length > 0){
        const obj = inputloginpara;
        const inputvalues = Array.from(obj);
        for(let i = 0;i<inputvalues.length;i++){
            loginparameter[inputvalues[i].getAttribute("name")] = unescape(inputvalues[i].value);
        }
    }
    const inputloginurl = document.getElementById("inputloginurl");
    if(inputloginurl != null){
        loginurl = unescape(inputloginurl.value);
    }
    const inputloginflagstr = document.getElementById("inputloginflagstr");
    if(inputloginflagstr != null){
        loginflagstr = unescape(inputloginflagstr.value);
    }
    const inputloginflagpage = document.getElementById("inputloginflagpage");
    if(inputloginflagpage != null){
        if(checkurl(unescape(inputloginflagpage.value))){
            loginflagpage = unescape(inputloginflagpage.value);
        }
        if(inputloginflagpage.value == ""){
            loginflagpage = inputloginflagpage.value;
        }
    }
}

// 現在選択している設定項目の色を濃くする関数
function colorchange(item){
    const items = document.querySelectorAll(".leftitems");
    for(let i = 0;i<items.length;i++){
        items[i].style.backgroundColor = "";
    }
    document.getElementById(item).style.backgroundColor = "#bab7b7";
}

// すべての設定情報をリセットする関数
function settingreset(){
    loginparameter = {};
    manualurls = [];
    loginurl = "";
    loginmethod = "";
    CSRFtokens = [];
    SESSIDNames = [];
    loginflagstr = "";
    loginflagpage = "";
}


let advanced_json_urls = null;
// 高度な巡回が選択されたときに実行する関数
function Advanced(){
    addformdata(true);
    colorchange("item6");
    const rightbox = removerightbox();
    let domain = null;
    advanced_json_urls = null;
    $.ajax({
        type: "post",
        url: "./SeleniumOperation.php",
        dataType: "json",
        data: {"state": "getdata"}
    }).done(function(res){
        // 設定されている情報を取得して画面に表示する
        const datas = res.pop();
        domain = datas["domain"];
        advanced_json_urls = JSON.parse(datas["json_urls"]);
        rightbox.insertAdjacentHTML("afterbegin", `<span class="settingtext">・ドメイン名 or IPアドレス</span><br>
                                                <input value="${escape(domain)}" id="inputdomain" class="settinginput" type="text">
                                                <button id="startbrowserbutton" style="font-size: 25px;" onclick="javascript: startbrowser()">ブラウザ起動</button><br>
                                                <button id="changedomainbutton" style="font-size: 25px;" onclick="javascript: changedomain()">ドメイン名変更</button>
                                                `);
    
        viewreqdatas(advanced_json_urls, rightbox, false);
    }).fail(function(res){
        console.log("Advanced機能の設定情報の取得に失敗しました");
    });
}


function viewreqdatas(advanced_json_urls, rightbox, loopflag){
    for(let i = 0;i<advanced_json_urls["requests"].length;i++){
        for(let key of Object.keys(advanced_json_urls["requests"][i])){
            const method = advanced_json_urls["requests"][i][key]["method"];
            const header = advanced_json_urls["requests"][i][key]["strheaders"];
            const body = advanced_json_urls["requests"][i][key]["body"];
            const methodcolor = methodcolors[method];
            rightbox.insertAdjacentHTML("beforeend", `<span class="viewurls">
                                                    <span class="viewmethod" style="color: ${methodcolor};">${method.toUpperCase()}</span><label class="viewurlitem">${key}</label>
                                                    <label class="viewremovebutton">
                                                    <a href="javascript: deladvancedurl(${i})">取消</a>
                                                    </label>
                                                    </span>
                                                    <div id="reqdetail${i}" class="reqdetailbox">${header}${body}
                                                    </div>`);
            
        }
    }
    // ブラウザが停止されている場合のみ詳細情報を表示できるようにする
    if(!loopflag){
        document.querySelectorAll(".viewurlitem").forEach((el) => {
            el.addEventListener("click", (el2) => {
                const label = el2.target;
                const span = label.parentElement;
                const reqdetailbox = span.nextElementSibling;
                $(reqdetailbox).slideToggle(500);
                const caret = span.querySelector(".fa-caret-right");
                $(caret).toggleClass("rotateon")
            })
        })
    }
}

let timerID2 = null;
let loopflag2 = false;
// 巡回用のブラウザを起動する関数
function startbrowser(){
    const domainval = document.getElementById("inputdomain").value;
    $.ajax({
        type: "post",
        url: "./SeleniumOperation.php",
        dataType: "json",
        data: {"state": "startbrowser", "domain": domainval}
    }).done(function(res){
        const rightbox = removerightbox();
        rightbox.insertAdjacentHTML("afterbegin", `<span class="settingtext">・ドメイン名 or IPアドレス</span><br>
                                                <h2>${escape(domainval)}</h2>
                                                <h3><a href="http://localhost:7900" target="_blank">ブラウザへアクセス</a></h3>
                                                <button id="startbrowserbutton" style="font-size: 25px;" onclick="javascript: startbrowser()">停止する</button>
                                                `);
        
        const startbrowserbutton = document.getElementById("startbrowserbutton");
        startbrowserbutton.textContent = "停止する";
        startbrowserbutton.onclick = "javascript: stopbrowser()";

        getadvanceddata();
        timerID2 = setInterval(getadvanceddata, 2000);
        loopflag2 = true;
    }).fail(function(res){
        console.log("seleniumブラウザの起動に失敗しました");
    });
}

// 巡回用ブラウザを停止する関数
function stopbrowser(){
    $.ajax({
        type: "post",
        url: "./SeleniumOperation.php",
        dataType: "json",
        data: {"state": "stopbrowser"}
    }).done(function(res){
        // ブラウザ用のプログラムが終了したら元の状態に戻す
        clearTimeout(timerID2);
        loopflag2 = false;

        Advanced();
    }).fail(function(res){
        console.log("seleniumブラウザの停止に失敗しました");
    });
}

// 巡回済みのURLを削除する関数
function deladvancedurl(index){
    advanced_json_urls["requests"].splice(index, 1);
    $.ajax({
        type: "post",
        url: "./SeleniumOperation.php",
        dataType: "json",
        data: {"state": "removedata", "json_urls": JSON.stringify(advanced_json_urls)}
    }).done(function(res){
        // ブラウザが起動中の場合は初期画面ではなく起動中の画面を再度生成しなおす
        if(loopflag2){
            getadvanceddata();
        }else{
            Advanced();
        }
    }).fail(function(res){
        console.log("Advancedのjson_urlsデータの削除に失敗しました");
    })
}

// 巡回したリクエストの情報をリアルタイムで取得する関数
function getadvanceddata(){
    $.ajax({
        type: "post",
        url: "./SeleniumOperation.php",
        dataType: "json",
        data: {"state": "getdata"}
    }).done(function(res){
        // 設定されている情報を取得して画面に表示する
        const datas = res.pop();
        const domainval = datas["domain"];
        const state =datas["state"];
        if(state == "False"){
            return;
        }
        advanced_json_urls = JSON.parse(datas["json_urls"]);
        const rightbox = removerightbox();
        rightbox.insertAdjacentHTML("afterbegin", `<span class="settingtext">・ドメイン名 or IPアドレス</span><br>
                                                <h2>${escape(domainval)}</h2>
                                                <h3><a href="http://localhost:7900" target="_blank">ブラウザへアクセス</a>(パスワード: secret)</h3>
                                                <button id="startbrowserbutton" style="font-size: 25px;" onclick="javascript: stopbrowser()">停止する</button>
                                                `);
    
        viewreqdatas(advanced_json_urls, rightbox, true);
    }).fail(function(res){
        console.log("Advanced機能の設定情報の取得に失敗しました");
    });
}

// ドメイン名を変更して巡回結果を初期化する関数
function changedomain(){
    const domainval = document.getElementById("inputdomain").value;
    $.ajax({
        type: "post",
        url: "./SeleniumOperation.php",
        dataType: "json",
        data: {"state": "changedomain", "domain": domainval}
    }).done(function(res){
        Advanced();
    }).fail(function(res){
        console.log("Advancedのjson_urlsデータの削除に失敗しました");
    })
}