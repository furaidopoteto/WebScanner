<?php
require("dbconnect.php");
session_start();
if(!isset($_SESSION['username'])){
    header('Location: login.php');
    exit;
}

$roomselect = null;
$error['count'] = null;
$year = null;
$month = null;
$day = null;

$roomprice = 7600;
$onedayprice = 5600;

//日付が選択された時の処理
if(!empty($_GET['month']) && !empty($_GET['day']) && !empty($_GET['year'])){
    $year = $_GET['year'];
    $month = $_GET['month'];
    $day = $_GET['day'];

    $now = date("Ymd");
    $checkdate = date("Ymd", strtotime($year. "/". $month. "/". $day));
    if($checkdate < $now){
        header('Location: yoyaku2.php');
        exit;
    }
    //選択された日付が満室の場合はエラーを返す
    $selectdate = date("Y-m-d", strtotime($year."/".$month."/".$day));
    $sumcheck = $data->prepare("SELECT SUM(roomcount) as cnt FROM data WHERE startdate=?");
    $sumcheck->execute(array($selectdate));
    $sumcheck = $sumcheck->fetch();
    if($sumcheck['cnt'] >= 50){
        header('Location: yoyaku2.php?error=count&year='. $year. '&month='. ($month-1));
        exit;
    }
    if(empty($sumcheck['cnt'])){
        $sumcheck['cnt'] = 0;
    }
    //空室の数だけセレクトボックスで選択できるようにするために空室を変数に格納
    $roomselect = 50-$sumcheck['cnt'];
}

//予約するボタンが押されたときの処理
if(!empty($_POST)){
    $roomcount = $_POST['roomselect'];
    $stays = $_POST['staysselect'];
    $peoplecount = $_POST['peopleselect'];

    //予約しようとした日付がすでに予約済みの日付の範囲内かどうかを調べる
    $checkstays = 0;
    if(!$stays <= 0){
        $checkstays = $stays-1;
    }
    $usersearch = $data->prepare("SELECT COUNT(*) AS cnt FROM data WHERE username=? AND startdate BETWEEN ? AND ?");
    $startsearch = date("Y-m-d", strtotime($year."/".$month."/".$day));
    $endsearch = date("Y-m-d", strtotime($year."/".$month."/".$day. " +". $checkstays. " day"));
    $usersearch->execute(array($_SESSION['username'], $startsearch, $endsearch));
    $usersearch = $usersearch->fetch();
    if($usersearch['cnt'] > 0){
        $error['myyoyaku'] = 'error';
        header('Location: yoyaku2.php?error=myyoyaku&year='. $year. '&month='. ($month-1));
        exit;
    }

    for($i = 1;$i<$stays;$i++){
        //宿泊数内の日付一つ一つに対して部屋数の合計を計算して満室を超える日付がないかを調べる
        $plusdate = date("Y-m-d", strtotime($year."/".$month."/".$day. " +". $i. " day"));
        $sumcheck = $data->prepare("SELECT SUM(roomcount) as cnt FROM data WHERE startdate=?");
        $sumcheck->execute(array($plusdate));
        $sumcheck = $sumcheck->fetch();
        if(empty($sumcheck['cnt'])){
            $sumcheck['cnt'] = 0;
        }
        if($sumcheck['cnt']+$roomcount > 50){
            $error['count'] = "error";
            header('Location: yoyaku2.php?error=count&year='. $year. '&month='. ($month-1));
            exit;
        }
    }
    if(empty($error['count']) && empty($error['myyoyaku'])){
        //満室を超える日付がなかった場合は宿泊する日付すべてをデータベースに保存する
        $price = $roomcount*$roomprice*$stays;
        if($stays <= 0){
            $price = $roomcount*$onedayprice;
        }
        for($i = 0;$i<$stays;$i++){
            $startdate = date("Y-m-d", strtotime($year."/".$month."/".$day. " +". $i. " day"));
            $enddate = date("Y-m-d", strtotime($year."/".$month."/".$day. " +". $stays. " day"));
            $insertdata = $data->prepare("INSERT INTO data (username, roomcount, peoplecount , startdate, enddate, stayscount, price, yoyakujikoku) VALUES (?, ? , ? , ?, ? , ?, ?, NOW())");
            $insertdata->execute(array($_SESSION['username'], $roomcount, $peoplecount , $startdate, $enddate, $stays, $price));
        }
        if($stays <= 0){
            $startdate = date("Y-m-d", strtotime($year."/".$month."/".$day. " +". $i. " day"));
            $enddate = date("Y-m-d", strtotime($year."/".$month."/".$day. " +". $stays. " day"));
            $insertdata = $data->prepare("INSERT INTO data (username, roomcount, peoplecount , startdate, enddate, stayscount, price, yoyakujikoku) VALUES (?, ? , ? , ?, ? , ?, ?, NOW())");
            $insertdata->execute(array($_SESSION['username'], $roomcount, $peoplecount , $startdate, $enddate, $stays, $price));
        }
        header('Location: success.php?success=insert');
        exit;
    }
}

?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel ="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <title>情報入力画面</title>
    <style>
        body{
            background-color: #e5e2dd;
        }
        .box{
            background-color: white;
            width: 450px;
            height: 320px;
            margin-left: auto;
            margin-right: auto;
            margin-top: 50px;
            font-size: 30px;
            border: solid 1px black;
            text-align: center;
            padding: 150px 30px;
        }
        select, .submitbutton{
            margin-top: 40px;
        }
        .title{
            display: inline-block;
        }
        select{
          font-size: 30px;
        }
        .submitbutton{
            font-size: 30px;
            width: 50%;
            transition: .5s ease;
        }
        .submitbutton:hover{
            background-color: green;
            opacity: .8;
        }

        .returnbutton{
            font-size: 100px;
            color: black;
            transition: .5s ease;
            position: absolute;
            top: 10px;
        }
        .returnbutton:hover{
            color: green;
        }

        #sumview{
            margin-top: 20px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <a class="returnbutton" href="yoyaku2.php"><i class="fas fa-arrow-left"></i></a>
    <div class="box">
        <form action="" method="POST">
            <span class="title">日付:<?php echo date("Y-m-d", strtotime($year."/".$month."/".$day));?></span><br>
            人数:<select name="peopleselect">
                <?php for($i = 1;$i<=50;$i++):?>
                    <option value="<?php echo $i;?>"><?php echo $i;?>人</option>
                <?php endfor;?>
            </select><br>
            部屋数:<select id="roomselect" name="roomselect" onchange="price()">
                <?php for($i = 1;$i<=$roomselect;$i++):?>
                    <option value="<?php echo $i;?>"><?php echo $i;?>部屋</option>
                <?php endfor;?>
            </select><br>
            宿泊数:<select id="staysselect" name="staysselect" onchange="price()">
                <option value="0">日帰り</option>
                <?php for($i = 1;$i<=4;$i++):?>
                    <option value="<?php echo $i;?>"><?php echo $i;?>泊<?php echo $i+1;?>日</option>
                <?php endfor;?>
            </select><br>
            <span id="sumview"></span><br>
            <input class="submitbutton" type="submit" value="予約する">
        </form>
    </div>
    <script>
        'use strict';

        const roomselect = document.getElementById('roomselect');
        const staysselect = document.getElementById('staysselect');
        const sumview = document.getElementById('sumview')

        let roomprice = 7600;
        let onedayprice = 5600;

        let price = () => {
            let roomcount = roomselect.value;
            let stayscount = staysselect.value;
            let sum = roomcount*stayscount*roomprice;
            if(stayscount <= 0){
                sum = roomcount*onedayprice;
            }
            sumview.textContent = `合計${sum}円`;
        }

        price();
    </script>
</body>
</html>