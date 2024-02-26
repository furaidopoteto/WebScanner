<?php
session_start();

if(!isset($_SESSION['username']) && isset($_COOKIE['name']) && isset($_COOKIE['pw'])){
    header('Location: login.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="./cssfile/header.css">
    <link rel ="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <title>グランドホテル</title>
    <style>
        .homebox{
            background-image: url("./img/hotelimg2.jpg");
            background-image: cover;
            width: 100%;
            height: 100%;
            position: absolute;
            top: 50px;
            left: 0;
        }
        #hometitle{
            color: white;
            text-align: center;
            font-size: 50px;
            padding: 250px;
            animation: 3s linear 1 loadanimation;
        }
        @keyframes loadanimation{
            0% {opacity: 0;};
            100% {opacity: 1;};
        }

        .homesubbox{
            width: 100%;
            height: 500px;
            margin-top: 52.3%;/* margin-top*/
        }
        .homesubbox2{
            width: 100%;
            height: 500px;
            display: flex;
            position: absolute;
            left: 0%;
            margin-top: 83.8%;/* margin-top*/
            background-color: #e5e2dd;
        }
        .homesubbox{
            position: absolute;
            left: 0;
            display: flex;
            background-color: #e5e2dd;
        }
        .homesubboximg{
            width: 80%;
            height: 100%;
            transition: 1s ease;
        }
        .homesubtitle{
            font-size: 40px;
        }
        .homesubboxsetumei{
            font-size: 25px;
        }
        .homesubboxsetumei, .homesubtitle{
            color: black;
            z-index: 2;
            width: 80%;
            text-align: center;
            margin-top: 50px;
        }
        .homesubbox3{
            padding-top: 50px;
            width: 100%;
            height: 450px;
            margin-top: 115.5%;/* margin-top*/
            position: absolute;
            left: 0;
            text-align: center;
            background-color: #e5e2dd;
        }
        .homesubbox3title{
            font-size: 50px;
        }
        .homesubbox3setumei{
            font-size: 25px;
        }

        .homesubbox, .homesubbox2, .homesubbox3{
            opacity: 0;
            transition: 2.5s ease;
        }

        .boxview1, .boxview2, .boxview3{
            opacity: 1;
        }
    </style>
</head>
<body>
    <?php include('./header.php');?>
    <div class="homebox">
        <h1 id="hometitle">グランドホテル<i class="fab fa-asymmetrik"></i></h1>
    </div>
    <div class="homesubbox">
        <span class="homesubboxsetumei"><span class="homesubtitle">外観</span><br>本ホテルでは庭に巨大なプールを完備していますので<br>
            いつでも楽しむことができます。<br>
            プールサイドにはテントがあり<br>バーベキューを楽しむこともできます</span>
        <img class="homesubboximg" src="./img/poolimg.jpg" alt="">
    </div>
    <div class="homesubbox2">
        <img class="homesubboximg" src="./img/steak.jpg">
        <span class="homesubboxsetumei"><span class="homesubtitle">ディナー</span><br>ディナーではシェフが厳選したものを<br>順番にお出しするコースメニューのほか、<br>
            ステーキやスパゲティなどお好きなものを<br>注文することもできます。</span>
    </div>
    <div class="homesubbox3">
        <span class="homesubbox3title">料金について</span><br>
        <span class="homesubbox3setumei">1部屋1泊につき: 7600円(日帰りの場合は5600円)<br>キャンセル料: 1000円</span><br>
        <span class="homesubbox3title">時間割について</span><br>
        <span class="homesubbox3setumei">チャックイン: 15:00～<br>
        ディナー: 18:00～20:00<br>
        チェックアウト: ～10:00(日帰りの方はその日の21:00まで)<br></span>
        <span class="homesubbox3footer">※日帰りの場合はディナーは付いておりません。<br>
        ※料金は部屋数×宿泊数×料金となっております。<br>
        ※現在の日付がチェックインの2日前以内になった場合はキャンセルはできません。</span><br>
    </div>
    <script src="./jquery-3.5.1.min.js"></script>
    <script>
        'use strict';

        const homesubbox = $('.homesubbox');
        const homesubbox2 = $('.homesubbox2');
        const homesubbox3 = $('.homesubbox3');
        //下に一定間隔スクロールした時の処理 参照: https://yuyauver98.me/scroll-show-hide-btn/
        $(window).on( 'scroll', function () {
        //スクロール位置を取得
        if($(this).scrollTop() < 100 ){
            homesubbox.removeClass('boxview1');
        }else{
            homesubbox.addClass('boxview1');
        }
        if($(this).scrollTop() < 700 ){
            homesubbox2.removeClass('boxview2');
        }else{
            homesubbox2.addClass('boxview2');
        }
        if($(this).scrollTop() < 1300 ){
            homesubbox3.removeClass('boxview3');
        }else{
            homesubbox3.addClass('boxview3');
        }
    });
    </script>
</body>
</html>