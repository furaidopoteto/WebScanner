<?php
require("../DBconnect.php");

$query = $db->query("SELECT * FROM scandata ORDER BY time DESC");
?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <link rel="icon" href="../favicons/favicon.ico">
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../hanbagu.css">
    <link rel="stylesheet" href="./CSS/indexstyle.css">
    <link rel="stylesheet" href="./CSS/setting.css">
    <link rel ="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@8"></script>
    <title>WebScanner</title>
</head>
<body>
    <div id="loadingbg">
        <div id="loadingimgbox">
            <img id="loadingjunkaiimg" src="./LoadingGIF/285.gif" alt=""><br>
            <span>巡回中...</span>
            <div id="junkaiurlbox"></div>
        </div>
    </div>
    <?php include("../hanbagu.php");?>

    <div id="settinginfo">
        <i class="fa-regular fa-circle-question" id="question"></i><br>
        <i class="fa-solid fa-gear" id="setting"></i><br>
        <span id="viewmanualurl">手動追加URL: 未設定</span>
        <span id="viewloginpara">ログイン情報: 未設定</span>
        <span id="viewsessidsetting">セッションCookie名: 未設定</span>
        <span id="viewcsrftokensetting">CSRFトークン: 未設定</span>
    </div>
    <div id="formbox">
        <div id="inputurlbox">
            <label class="inputlabel">URL: <input id="inputurl" type="text" name="url" required></label>
        </div>
        
        <div class="inputlabel">
            <span id="checkboxtitle">自動巡回: </span>
            <span id="onofftitle">ON</span>
            <div class="toggle AutoPatrolButton checked">
                <input type="checkbox" name="check" />
            </div>
            
            <div id="advancedcheck">
                <span id="checkboxtitle">高度な巡回: </span>
                <span id="onofftitle2">OFF</span>
                <div class="toggle AdvancedButton">
                    <input type="checkbox" name="check2" />
                </div>
            </div>
        </div><br>
        <input id="startbutton" type="submit" value="診断開始" onclick="confirmcheck()">
    </div>
    <div id="attackinfobox">
        <span id="infotitle">診断中</span>
        <span class="alertcntbox"><i class="fa-solid fa-flag"></i><span id="alertcnt">0</span></span><br>
        <div id="loadingbox">
            <img id="loadingimg" src="./LoadingGIF/245.gif">
        </div>
        <span id="percent"></span><br>
        対象URL: <span id="domain"></span><br>
        パラメータ: <span id="parameter"></span><br>
    </div>
    <div id="attackurlinfo">
        
    </div>
    <div id="scanviewbox">
        <?php foreach($query as $index):?>
            <div class="scanviewitembox">
                <span class="scanviewdomain scanviewitems">診断URL: <?php echo $index['domain'];?></span><br>
                <span class="scanviewalertcnt scanviewitems">検出数: <?php echo $index['alertcnt'];?></span><br>
                <span class="scanviewtime scanviewitems">診断時刻: <?php echo $index['time'];?></span>
                <span class="scanviewtime scanid" style="display: none"><?php echo $index['scanid'];?></span>
            </div>
        <?php endforeach;?>
    </div>
    <script src="../jquery-3.5.1.min.js"></script>
    <script src="
https://cdn.jsdelivr.net/npm/echarts@5.4.1/dist/echarts.min.js
"></script>
    <script src="../hanbagu.js"></script>
    <script src="./JS/AttackView.js"></script>
    <script src="./JS/Question.js"></script>
    <script>
        'use strict';

        const scanviewitemboxs = document.querySelectorAll(".scanviewitembox");
        scanviewitemboxs.forEach(function(item){
            item.addEventListener("click", function(e){
                const scanid = item.querySelector(".scanid").textContent;
                location.href = "./ViewScanData.php?scanid="+scanid;
            })
        })
    </script>
</body>
</html>