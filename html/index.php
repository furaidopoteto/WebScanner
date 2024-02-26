<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>index</title>
    <style>
        *{
            background-color: #F4F5F7;
        }
        #box{
            width: 700px;
            margin-left: auto;
            margin-right: auto;
            margin-top: 30vh
        }
        .linkbutton{
            display: inline-block;
            font-size: 30px;
            padding: 30px;
            margin-bottom: 50px;
            background-color: gray;
            border-radius: 10px;
            text-decoration: none;
            color: black;
        }
        .linkbutton:hover{
            opacity: .7;
        }
    </style>
</head>
<body>
    <div id="box">
        <a class="linkbutton" href="./SecurityApp/WebAppScanner/index.php">診断アプリ</a><br>
        <a class="linkbutton" href="./yoyakuDB3/home.php">診断テスト用サイト</a><br>
        <a class="linkbutton" href="http://127.0.0.1:3001/">phpmyadmin</a>
    </div>
</body>
</html>