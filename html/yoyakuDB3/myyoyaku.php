<?php
require('dbconnect.php');
session_start();

$array = [];
if(!isset($_SESSION['username'])){
    header('Location: login.php');
    exit;
}else{
    //現在の日付以降の予約情報を取得
    $search = $data->prepare('SELECT * FROM data WHERE username=? AND startdate>=CURRENT_DATE() ORDER BY startdate');
    $search->execute(array($_SESSION['username']));
}
?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel ="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <title>ご予約確認</title>
    <style>
        body{
            background-color: #e5e2dd;
        }
        .title{
            text-align: center;
        }
        .box{
            background-color: white;
            margin-left: auto;
            margin-right: auto;
            border: solid 1px black;
            width: 1200px;
            text-align: center;
        }
        .column{
            font-size: 23px;
            width: 14.2%;
            display: inline-block;
            border-right: solid 1px black;
        }
        .subbox{
            display: flex;
            border-bottom: solid 1px black;
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
        .cancelbutton{
            font-size: 24px;
        }
    </style>
</head>
<body>
    <a class="returnbutton" href="home.php"><i class="fas fa-arrow-left"></i></a>
    <h1 class="title"><?php echo $_SESSION['username'];?>様のご予約状況</h1>
    <div class="box">
        <div class="subbox">
            <span class="column">チェックイン</span>
            <span class="column">人数</span>
            <span class="column">部屋数</span>
            <span class="column">宿泊数</span>
            <span class="column">チェックアウト</span>
            <span class="column">料金</span>
            <span class="column"></span>
        </div>
        <?php foreach($search as $index):?>
            <?php
            //最初の宿泊日だけを表示させるようにする
            $checkin = "15:00～";
            $checkout = "～10:00";
            if($index['stayscount'] <= 0){
                $checkin = "15:00～";
                $checkout = "～21:00";
            }

            //チェックアウトからチェックインの日付を引いて宿泊数と比較することで宿泊日付の一番最初だけ取得するようにする
            $startdate = strtotime($index['startdate']);
            $enddate = strtotime($index['enddate']);
            $search = ($enddate - $startdate)/(60*60*24);
            if($search != $index['stayscount']){
                continue;
            }
            $stays = $index['stayscount']. "泊". ($index['stayscount']+1). "日";
            if($index['stayscount'] <= 0){
                $stays = "日帰り";
            }

            //現在の日付がチェックインの日付の2日前以内だった場合はキャンセルボタンを非表示にする
            $cancelcheck = true;
            $now = new DateTime();//PHP5.2.0から新しく追加されたDateTimeオブジェクト 参照: https://www.sejuku.net/blog/21496
            $minusdate = new DateTime($index['startdate']);
            //DateTimeオブジェクトの日付の操作方法は 参照: https://qiita.com/thiagomatsui/items/619775a96dce38bc5060
            $minusdate->modify("-2 day");
            if($now >= $minusdate){
                $cancelcheck = false;
            }
            ?>
            <div class="subbox">
                <span class="column"><?php echo $index['startdate'];?> <?php echo $checkin;?></span>
                <span class="column"><?php echo $index['peoplecount'];?>名</span>
                <span class="column"><?php echo $index['roomcount'];?>部屋</span>
                <span class="column"><?php echo $stays;?></span>
                <span class="column"><?php echo $index['enddate'];?><br> <?php echo $checkout;?></span>
                <span class="column"><?php echo $index['price'];?>円</span>
                <?php if($cancelcheck):?>
                    <a class="cancelbutton" href='javascript:yoyakudelete("delete.php?username=<?php echo $index['username'];?>&enddate=<?php echo $index['enddate'];?>&startdate=<?php echo $index['startdate'];?>")'>キャンセル</a>
                <?php endif;?>
            </div>
        <?php endforeach;?>
    </div>
    <script>
        'use strict';

        let yoyakudelete = (url) => {
            if(window.confirm("本当にキャンセルしますか?(キャンセル料1000円がかかります)")){
                location.href = url
            }
        }
    </script>
</body>
</html>