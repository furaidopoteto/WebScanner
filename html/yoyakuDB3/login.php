<?php
require('dbconnect.php');
session_start();

// セキュリティシステムのテストを行うためSQLインジェクションとXSSの脆弱性を埋め込んである(アカウント作成画面も同様)
if(isset($_COOKIE['name'])){
    $_POST['name'] = $_COOKIE['name'];
    $_POST['pw'] = $_COOKIE['pw'];
}

if(empty($_GET['redirect'])){
    header('Location: login.php?redirect=home.php');
    exit;
}

if(isset($_COOKIE['count'])){
    if($_COOKIE['count'] >= 100000){// 元々の回数制限は5回
        header('Location: loack.php');
        exit;
    }
}else{
    setcookie('count', 0, time()+60*60*24);
}
if(!empty($_POST)){
    $name = $_POST['name'];
    $pw = $_POST['pw'];

    //$check = $data->prepare('SELECT COUNT(*) AS cnt FROM account WHERE username=? AND password=?');
    //$check->execute(array($name, sha1($pw)));
    $check = $data->query('SELECT COUNT(*) AS cnt FROM account WHERE username="'. $name. '" AND password="'. sha1($pw). '"');// SQLinjection
    $check = $check->fetch();
    if($check['cnt'] == 1){
        if($_POST['checkbox'] == "on"){
            setcookie("name", $name, time()+60*60*24*7);
            setcookie("pw", $pw, time()+60*60*24*7);
        }
        $_SESSION['username'] = $name;
        if(preg_match("/.*http.*/", $_POST['redirect']) || preg_match("/.*\/\/.*/", $_POST['redirect'])){
            header('Location: home.php');
            exit;
        }
        header('Location: '. $_POST['redirect']);
        exit;
    }else{
        $_COOKIE['count']++;
        setcookie('count', $_COOKIE['count'], time()+60*60*24);
        if($_COOKIE['count'] >= 100000){// 元々の回数制限は5回
            header('Location: loack.php');
            exit;
        }
        $error['name'] = "type";
    }
}

function escape($val){
    return htmlspecialchars($val, ENT_QUOTES);
}
?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ログイン</title>
    <link rel="stylesheet" href="./cssfile/loginstyle.css">
</head>
<body>
        <?php
        $inputname = "";
        if(!empty($_POST)){
            $inputname = $_POST['name'];
        }
        ?>
        <div class="box">
            <form action="" method="POST">
                <span class="title">ログイン<br>ご予約にはログインが必要です</span><br>
                <input id="inputtext" class="inputfield" type="text" name="name" placeholder="ユーザー名" required onkeyup="keycheck()" value="<?php echo $inputname;?>"><br>
                <input id="inputpw" class="inputfield" type="password" name="pw" placeholder="パスワード※4文字以上" onkeyup="keycheck()" required><br>
                <label id="loginlabel">次回以降自動ログインする<input id="logincheckbox" type="checkbox" name="checkbox" value="on"></label><br>
                <?php if(!empty($_POST) && $error['name'] == "type"):?>
                    <span class="error">* ユーザー名またはパスワードが違います</span><br>
                <?php endif;?>
                <input type="hidden" name="redirect" value="<?php echo $_GET['redirect'];?>">
                <input id="submitbutton" type="submit" value="ログイン" disabled><br>
                <a href="account.php" class="abutton">アカウントをお持ちでない場合</a><br>
                <a href="home.php" class="abutton">トップページへ戻る</a>
            </form>
        </div>
        <script src="./jquery-3.5.1.min.js"></script>
        <script>
            'use strict';

            const text = document.getElementById('inputtext');
            const pw = document.getElementById('inputpw');
            const submitbutton = document.getElementById('submitbutton');

            let keycheck = () => {
                let textval = text.value;
                let pwval = pw.value;
                if(pwval.length >= 4 && textval.length > 0){
                    submitbutton.disabled = false;
                }else{
                    submitbutton.disabled = true;
                }
            }
        </script>
</body>
</html>