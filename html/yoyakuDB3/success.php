<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>success</title>
    <style>
        body{
            background-color: #e5e2dd;
        }
        .box{
            height: 500px;
            width: 800px;
            background-color: white;
            text-align: center;
            margin-left: auto;
            margin-right: auto;
            margin-top: 100px;
        }
        .title{
            display: inline-block;
            margin-top: 100px;
        }
    </style>
</head>
<body>
    <div class="box">
        <?php
        $href = "home.php";
        $title = "トップページへ";
        if(!empty($_GET['rootdelete'])){
            $href = "adminview.php";
            $title = "管理画面へ";
        }
        if(!empty($_GET['success'])){
            if($_GET['success'] == "delete"){
                echo "<h1 class='title'>キャンセルが完了しました<br><a href='". $href . "'>". $title . "</a></h1>";
            }else if($_GET['success'] == 'insert'){
                echo "<h1 class='title'>ご予約ありがとうございました!<br>ご予約状況はトップページからご確認できます<br><a href='home.php'>トップページへ</a></h1>";
            }
        }else{
            header('Location: home.php');
            exit;
        }
        ?>
    </div>
</body>
</html>