<?php
require("../DBconnect.php");

if(!empty($_POST)){
    if($_POST['formnum'] == -1){
        // メイン画面でスキャンを表示するためのデータを保存
        $insert = $db->prepare("INSERT INTO scandata (scanid, domain, alertcnt, searchurls_json, Transition_image_path, time) VALUES (?, ?, 0, ?, ?, NOW())");
        $insert->execute(array($_POST['scanid'], $_POST['domain'], json_encode($_POST['searchurls']), $_POST['pdffilepath']));
    }
    
    // 詳細情報を表示するためのデータを保存
    $scanid = $db->query("SELECT MAX(scanid) as maxscanid FROM scandata");
    $scanid = $scanid->fetch();

    $riskindex = 0;

    if(isset($_POST['alertattacks'])){
        for($i = 0;$i<count($_POST['alertattacks']);$i++){
            $insert2 = $db->prepare("INSERT INTO scanalertdata (id, scanid, formnum, attackname, parameter, url, motourl, method, risk, errortext, imgpath, time) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())");
            $insert2->execute(array($scanid['maxscanid'], $_POST['formnum'], $_POST['alertattacks'][$i], $_POST['attackparameters'][$i], $_POST['requesturls'][$i], $_POST['requestmotourls'][$i], $_POST['requestmethods'][$i], $_POST['risks'][$i], $_POST['errortexts'][$i], $_POST['alertimgpath'][$i]));
        }
        $riskindex = count($_POST['alertattacks']);
    }
    if(isset($_POST['headeralertnames'])){
        for($i = 0;$i<count($_POST['headeralertnames']);$i++){
            $insert2 = $db->prepare("INSERT INTO scanalertdata (id, scanid, formnum, attackname, parameter, url, motourl, method, risk, errortext, imgpath, time) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())");
            $insert2->execute(array($scanid['maxscanid'], $_POST['formnum'], $_POST['headeralertnames'][$i], "", $_POST['headeralerturls'][$i], $_POST['headeralertmotourls'][$i], $_POST['headeralertmethods'][$i], $_POST['risks'][$i+$riskindex], $_POST['errortexts'][$i], ""));
        }
    }

    $alertcnt = $db->prepare("SELECT COUNT(*) AS cnt FROM scanalertdata WHERE scanid=?");
    $alertcnt->execute(array($scanid['maxscanid']));
    $alertcnt = $alertcnt->fetch();
    $newalertcnt = $db->prepare("UPDATE scandata SET alertcnt=? WHERE scanid=?");
    $newalertcnt->execute(array($alertcnt['cnt'], $scanid['maxscanid']));
}
?>