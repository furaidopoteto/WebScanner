<?php
require("../DBconnect.php");

if(!empty($_POST["state"])){
    if($_POST["state"] == "getdata"){
        $query = $db->query("SELECT * FROM advanced");
        $query = $query->fetchAll();
        echo json_encode($query);
        exit;
    }

    if($_POST["state"] == "stopbrowser"){
        $update = $db->prepare("UPDATE advanced SET state=?");
        $update->execute(array("False"));
        echo json_encode(["200" => "停止完了"]);
    }

    if($_POST["state"] == "removedata"){
        $update = $db->prepare("UPDATE advanced SET json_urls=?");
        $update->execute(array($_POST["json_urls"]));
        echo json_encode(["200" => "削除完了"]);
        exit;
    }

    if($_POST["state"] == "startbrowser"){
        $update = $db->prepare("UPDATE advanced SET state=?, domain=?");
        $update->execute(array("True", $_POST["domain"]));
        // seleniumコンテナに接続して、selenium-wireを起動するPythonを非同期で実行する
        exec("python3 ./Python/Advanced.py > /dev/null &");
        echo json_encode(["200" => "起動完了"]);
        exit;
    }

    if($_POST["state"] == "changedomain"){
        $update = $db->prepare("UPDATE advanced SET domain=?, json_urls='{\"requests\": []}'");
        $update->execute(array($_POST["domain"]));
        echo json_encode(["200" => "変更完了"]);
        exit;
    }
}
?>