<?php
require("../DBconnect.php");

if(isset($_POST['scanid']) && isset($_POST['getrisk'])){
    // スキャン結果の画面上部にリスク別検出数を表示するためのデータを取得する処理
    $check = $db->prepare("SELECT COUNT(*) AS cnt FROM scandata WHERE scanid=?");
    $check->execute(array($_POST['scanid']));
    $check = $check->fetch();
    if($check['cnt'] <= 0){
        header('Location: ./index.php');
        exit;
    }
    $data = ["Info" => 0, "Low" => 0, "Medium" => 0, "High" => 0, "Critical" => 0];
    $query = $db->prepare("SELECT risk, COUNT(*) AS cnt FROM scanalertdata WHERE scanid=? GROUP BY risk");
    $query->execute(array($_POST['scanid']));
    foreach($query as $index){
        $data[$index['risk']] += $index['cnt'];
    }
    $json = json_encode($data);
    echo $json;
    exit;
}
/*
else if(isset($_POST['scanid']) && isset($_POST['urls'])){
    // ページ別絞り込み画面のページとスクショ一覧を表示するために必要なデータを取得するための処理
    $check = $db->prepare("SELECT COUNT(*) AS cnt FROM scandata WHERE scanid=?");
    $check->execute(array($_POST['scanid']));
    $check = $check->fetch();
    if($check['cnt'] <= 0){
        header('Location: ./index.php');
        exit;
    }
    $data = [];
    $urls = json_decode($_POST['urls']);
    $query = $db->prepare("SELECT * FROM screendata WHERE scanid=?");
    $query->execute(array($_POST['scanid']));
    foreach($query as $index){
        if(in_array($index['pageurl'], $urls)){
            if(!array_key_exists($index['pageurl'], $data)){
                $data[$index['pageurl']] = [];
            }
            array_push($data[$index['pageurl']], $index['imgpath']);
            array_push($data[$index['pageurl']], $index['pagetitle']);
        }
    }
    $json = json_encode($data);
    echo $json;
}*/
else if(isset($_POST['scanid'])){
    // 巡回した全てのURLのデータを取得するための処理
    $check = $db->prepare("SELECT COUNT(*) AS cnt FROM scandata WHERE scanid=?");
    $check->execute(array($_POST['scanid']));
    $check = $check->fetch();
    if($check['cnt'] <= 0){
        header('Location: ./index.php');
        exit;
    }
    $data = [];
    $query = $db->prepare("SELECT * FROM scandata WHERE scanid=?");
    $query->execute(array($_POST['scanid']));
    $urls = json_decode($query->fetch()['searchurls_json']);
    foreach($urls as $index){
        array_push($data, $index);
    }
    $json = json_encode($data);
    echo $json;
    exit;
}
?>