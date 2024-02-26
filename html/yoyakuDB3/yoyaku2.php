<?php
require('dbconnect.php');
session_start();
if(!isset($_SESSION['username'])){
    header('Location: login.php');
    exit;
}

$array = [];
if(!isset($_GET['month']) || !isset($_GET['year'])){
    //URLパラメーターがない場合は現在の年と月を表示する
    if(isset($_GET['month'])){
        $_GET['year'] = date("Y");
        $_GET['month']--;
    }else{
        $_GET['year'] = date("Y");
        $_GET['month'] = date('m');
        $_GET['month']--;
    }
}
if(isset($_GET['month']) && isset($_GET['year'])){
    if($_GET['month'] > 11 || $_GET['month'] < 0){
        $_GET['year'] = date("Y");
        $_GET['month'] = date('m');
        $_GET['month']--;
    }
    //URLパラメーターの年と月をもとに日付一つ一つを検索して部屋数の合計を配列に格納していく
    for($i = 1;$i<=31;$i++){
        $year = $_GET['year'];
        $month = $_GET['month']+1;
        $date = date("Ymd", strtotime($year. "/". $month. "/". $i));
        //SQLで日付を指定した単位で検索する 参照: https://www.searchlight8.com/mysql-year-month-date_format/
        $search = $data->query("SELECT SUM(roomcount) as cnt FROM data WHERE DATE_FORMAT(startdate, '%Y%m%d')='". $date. "'");
        $search = $search->fetch();
        if(empty($search['cnt'])){
            $search['cnt'] = 0;
        }
        array_push($array, $search['cnt']);
    }
}
?>
<!DOCTYPE html>
<html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel ="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
        <title>予約画面</title>
        <style>
            body{
                background-color: #e5e2dd;
            }
            #box{
                width: 700px;
                margin-left: auto;
                margin-right: auto;
            }
            .nullday{
                text-align: center;
            }
            .header{
                font-size: 35px;
                text-align: center;
                display: flex;
                justify-content: space-between;/* 均等幅で横並びにする */
            }
            .header i{
                padding: 2px;
                font-size: 40px;
                color:#4db56a;
                border: solid 5px #4db56a;
                border-radius: 100%;
            }
            .header i:hover{
                color: blue;
                border-color: blue;
            }
            .year{
                text-align: center;
                font-size: 30px;
                display: block;
            }

            .subbox{
                display: inline-block;
                height: 100px;
                width: 14%;
                text-align: center;
                margin-bottom: 10px;
            }
            .subbox, .weekbox{
                font-size: 25px;
                border: solid 1px black;
            }
            .weekbox{
                border-bottom: #4db56a solid 4px;
                margin-bottom: 10px;
                display: inline-block;
                height: 40px;
                width: 14%;
                text-align: center;
            }
            .weeknumber0{
                color: red;
            }
            .weeknumber6{
                color: blue;
            }

            .error{
                font-size: 30px;
                color: red;
                text-align: center;
                display: block;
            }

            .notover{
                
            }
            .over{
                background-color: red;
            }
            .count{
                color: black;
            }
            .viewday{
                text-decoration: none;
                height: 100%;
                width: 100%;
                display: inline-block;
                transition: .5s ease;
            }
            .viewday:hover{
                background-color: #4db56a;
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
        </style>
    </head>
    <body>
        <a class="returnbutton" href="home.php"><i class="fas fa-arrow-left"></i></a>
        <?php if(!empty($_GET['error']) && $_GET['error'] == "count"):?>
            <span class="error">* 宿泊日数内に満室の日付があります</span><br>
        <?php elseif(!empty($_GET['error']) && $_GET['error'] == 'myyoyaku'):?>
            <span class="error">* すでに予約済みの日付が含まれています</span><br>
        <?php endif;?>
        <div id="box">
            
        </div>
        <script src="./jquery-3.5.1.min.js"></script>
        <script>
            'use strict';

            const box = document.getElementById('box');
            const weekname = ["日", "月", '火', '水', '木', '金', '土'];
            let date = new Date();
            let selectmonth = 0;
            let selectyear = 0;
            let countarray = <?php echo json_encode($array);?>//phpで格納した各日付の部屋数の合計をjavascriptの変数で取得

            //カレンダーの作成
            let createbox = (setyear, setmonth) => {
                selectmonth = setmonth;
                selectyear = setyear;
                while(box.firstChild){
                    box.removeChild(box.firstChild);
                }

                date = new Date();
                let nowmonth = date.getMonth();
                let nowyear = date.getFullYear();

                if(setyear <= nowyear && setmonth < nowmonth){
                    location.href = "yoyaku2.php";
                }

                //現在の月以外の日付の場合はすべての日付を表示
                if(nowmonth != setmonth){
                    date.setDate(1);
                }
                
                date.setMonth(setmonth);

                if(setyear <= nowyear){
                    setyear = nowyear;
                }else{
                    date.setFullYear(setyear);
                }
                box.insertAdjacentHTML("beforeend", `<span class='year'>${setyear}年</span><div class="header"><a href="javascript:changemonth('minus')"><i class="fas fa-arrow-left"></i></a>
                <span class='title'>${setmonth+1}月</span>
                <a href="javascript:changemonth('plus')"><i class="fas fa-arrow-right"></i></a></div>`);

                for(let i = 0;i<7;i++){
                    box.insertAdjacentHTML("beforeend", `<div class="weekbox weeknumber${i}"><span class="weekname">${weekname[i]}</span></div>`);
                }
                box.insertAdjacentHTML("beforeend", `<br>`);
                
                const fastweek = date.getDay();
                //空いている日付を×にして配置を整える
                if(fastweek < 7){
                    for(let i = 0;i<fastweek;i++){
                        box.insertAdjacentHTML("beforeend", `<div class="subbox nullday"><br>×</div>`);
                    }
                }
                
                //月が替わるまで日付を加算していって表示する
                for(let i = 0;i<31;i++){
                    let overcheck = "notover";
                    if(i != 0){
                        date.setDate(date.getDate()+1);
                    }
                    const day = date.getDate();
                    const month = date.getMonth()+1;
                    const week = date.getDay();
                    if(month != setmonth+1){
                        console.log("ループを抜けました");
                        break;
                    }
                    if(countarray[day-1] >= 50){
                        overcheck = "over";
                    }
                    if(week == 3){
                        box.insertAdjacentHTML("beforeend", 
                        `<div class="subbox subboxday${day} ${overcheck}">
                        <a class="">${day}<br>
                        <span class="count" style="color: red">定休日</span></a>
                        </div>`);
                    }else{
                        box.insertAdjacentHTML("beforeend", 
                        `<div class="subbox subboxday${day} ${overcheck}">
                        <a class="viewday" href="./inputdata.php?year=${setyear}&month=${month}&day=${day}">${day}<br>
                        <span class="count">空室${50-countarray[day-1]}</span></a>
                        </div>`);
                    }
                    if(week >= 6){
                        box.insertAdjacentHTML("beforeend", "<br>");
                    }
                }
            }

            let changemonth = (change) => {
                if(change == 'minus'){
                    let minusmonth = selectmonth-1;
                    date = new Date();
                    //年をまたぐ場合はselectyearを-1する
                    if(minusmonth < 0){
                        selectyear--;
                        //現在の年より前になる場合は現在の年をselectyearに格納して元の月のままにする
                        if(selectyear < date.getFullYear()){
                            selectyear = date.getFullYear();
                            minusmonth++;
                        }else{
                            minusmonth = 11;
                        }
                    }
                    location.href = "./yoyaku2.php?month="+minusmonth+"&year="+selectyear;
                }else{
                    let plusmonth = selectmonth+1;
                    //プラスに年をまたぐ場合はselectyearを+1にして月を0(1月)にする
                    if(plusmonth > 11){
                        selectyear++;
                        plusmonth = 0;
                    }
                    location.href = "./yoyaku2.php?month="+plusmonth+"&year="+selectyear;;
                }
            }

            <?php if(isset($_GET['month'])):?>
                createbox(<?php echo $_GET['year'];?>, <?php echo $_GET['month'];?>);
            <?php else:?>
                createbox(date.getFullYear(), date.getMonth());
            <?php endif;?>
        </script>
    </body>
</html>