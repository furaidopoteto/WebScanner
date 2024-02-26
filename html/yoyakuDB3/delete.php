<?php
require('dbconnect.php');
session_start();

if(isset($_SESSION['personID']) && !empty($_GET['username']) && !empty($_GET['enddate'])){
    $search = $data->prepare("SELECT COUNT(*) AS cnt FROM data WHERE username=? AND enddate=?");
    $search->execute(array($_GET['username'], $_GET['enddate']));
    $search = $search->fetch();
    if($search['cnt'] <= 0){
        header('Location: adminview.php');
        exit;
    }
    $delete = $data->prepare('DELETE FROM data WHERE username=? AND enddate=?');
    $delete->execute(array($_GET['username'], $_GET['enddate']));
    header('Location: success.php?success=delete&rootdelete=true');
    exit;
}
if(isset($_SESSION['username']) && !empty($_GET['username']) && !empty($_GET['enddate']) && !empty($_GET['startdate'])){
    $datecheck = true;
    $now = new DateTime();
    $startdate = new DateTime($_GET['startdate']);
    if($startdate <= $now){
        $datecheck = false;
    }
    $startdate->modify("-2 day");
    if($now >= $startdate){
        $datecheck = false;
    }
    if($_SESSION['username'] == $_GET['username'] && $datecheck){
        $search = $data->prepare("SELECT COUNT(*) AS cnt FROM data WHERE username=? AND enddate=?");
        $search->execute(array($_GET['username'], $_GET['enddate']));
        $search = $search->fetch();
        if($search['cnt'] <= 0){
            header('Location: home.php');
            exit;
        }
        $delete = $data->prepare('DELETE FROM data WHERE username=? AND enddate=?');
        $delete->execute(array($_GET['username'], $_GET['enddate']));
        header('Location: success.php?success=delete');
        exit;
    }else{
        header('Location: home.php');
        exit;
    }
}else{
    header('Location: home.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>キャンセル</title>
</head>
<body>
    
</body>
</html>