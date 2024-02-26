<?php
require('dbconnect.php');

if(!empty($_POST)){
    $name = $_POST['name'];
    $pw = $_POST['pw'];
    $pwcheck = $_POST['pwcheck'];
    $error['name'] = "";
    $error["pw"] = "";
    $error['pwcheck'] = "";

    if($pw != $pwcheck){
        $error['pwcheck'] = "error";
    }
    if($name == $pw){
        $error["pw"] = "error";
    }
    $check = $data->prepare("SELECT COUNT(*) AS cnt FROM account WHERE username=?");
    $check->execute(array($name));
    $check = $check->fetch();
    if($check['cnt'] > 0){
        $error['name'] = "error";
    }
    if(empty($error['name']) && empty($error['pwcheck']) && empty($error["pw"])){
        $insert = $data->prepare('INSERT INTO account (username, password, time) VALUES (?, ?, NOW())');
        $insert->execute(array($name, sha1($pw)));
        header('Location: login.php');
        exit;
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
        <title>アカウント作成</title>
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
                <span class="title">アカウント作成</span><br>
                <input id="inputtext" class="inputfield" type="text" name="name" placeholder="ユーザー名" required onkeyup="keycheck()" value="<?php echo $inputname;?>"><br>
                <?php if(!empty($_POST) && $error['name'] == "error"):?>
                    <span class="error">* 指定したユーザー名は既に使われています</span><br>
                <?php endif;?>
                <input id="inputpw" class="inputfield" type="password" name="pw" placeholder="パスワード※4文字以上" onkeyup="keycheck()" required><br>
                <input id="inputpwcheck" class="inputfield" type="password" name="pwcheck" placeholder="パスワード確認" onkeyup="keycheck()" required><br>
                <?php if(!empty($_POST) && $error['pwcheck'] == "error"):?>
                    <span class="error">* パスワード確認の値が違います</span><br>
                <?php endif;?>
                <?php if(!empty($_POST) && $error['pw'] == "error"):?>
                    <span class="error">* ユーザ名と同一のパスワードは設定できません</span><br>
                <?php endif;?>
                <input id="submitbutton" type="submit" value="アカウントを作成する" disabled><br>
                <a href="login.php" class="abutton">ログイン画面へ</a><br>
                <a href="home.php" class="abutton">トップページへ戻る</a>
            </form>
        </div>
        <script src="./jquery-3.5.1.min.js"></script>
        <script>
            'use strict';

            const text = document.getElementById('inputtext');
            const pwcheck = document.getElementById('inputpwcheck');
            const pw = document.getElementById('inputpw');
            const submitbutton = document.getElementById('submitbutton');

            let keycheck = () => {
                let textval = text.value;
                let pwcheckval = pwcheck.value;
                let pwval = pw.value;
                if(pwval.length >= 4 && textval.length > 0 && pwcheckval.length > 0){
                    submitbutton.disabled = false;
                }else{
                    submitbutton.disabled = true;
                }
            }
        </script>
    </body>
</html>