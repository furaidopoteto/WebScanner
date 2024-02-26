<?php
require("../DBconnect.php");

$flawNames = ["XSS", "SQLインジェクション攻撃", "X-Frame-Options", "Content-Security-Policy", "Secure", "HttpOnly",
              "バージョン情報の漏洩", "HTTPによる通信", "ディレクトリリスティング", "OSコマンドインジェクション", "ディレクトリトラバーサル",
              "オープンリダイレクト", "HTTPヘッダインジェクション", "不要なエラーメッセージ", "CSRFトークンの有無", "DOM Based XSS",
              "HTTPステータスコード500-内部エラー"];

// 危険度を表す文字列の色を格納する配列
$colors = ["Info" => "gray", "Low" => "#0055ff", "Medium" => "orange", "High" => "red", "Critical" => "#ad0202"];

// 各脆弱性に対する説明文を格納する配列
$message = [$flawNames[0] => "当該URLにXSSの脆弱性が発見されました。ユーザからの入力を出力する箇所に適切なエスケープ処理を施す必要があります。",
    $flawNames[1] => "当該URLにSQLインジェクション攻撃の脆弱性が発見されました。ユーザからの入力に対して適切なエスケープ処理を施す必要があります。",
    $flawNames[2] => "当該URLのHTTPレスポンスヘッダにX-Frame-Optionsが付与されていませんでした。クリックジャッキングを防ぐ効果がありますので付与することを推奨します。",
    $flawNames[3] => "当該URLのHTTPレスポンスヘッダにContent-Security-Policyが付与されていませんでした。XSSやインジェクション攻撃など様々な攻撃を防ぐ効果がありますので付与することを推奨します。",
    $flawNames[4] => "セッションIDにSecure属性が付与されていませんでした。セッションIDが盗聴される危険性がありますので付与することを推奨します。",
    $flawNames[5] => "セッションIDにHttpOnly属性が付与されていませんでした。セッションID流出のリスクを軽減することができるので付与することを推奨します。",
    $flawNames[6] => "レスポンスヘッダにサーバなどのバージョン情報が見えてしまっている状態です。httpd.confファイルを編集してバージョン情報を隠すことを推奨します。",
    $flawNames[7] => "当該ページ内の通信が暗号化されておらず盗聴の危険性があります。SSL/TLSで暗号化したHTTPS通信にしていただくことを推奨します。",
    $flawNames[8] => "サーバ内のファイルやディレクトリの構造が閲覧可能な状態になっています。indexファイルなどを設置することでディレクトリ構造を隠すことを推奨します。",
    $flawNames[9] => "当該ページ内に攻撃者が任意のコマンドを実行できる状態でした。入力文字列のチェックやOSのコマンドを呼び出す関数の使用をやめることなどを推奨します。",
    $flawNames[10] => "パス指定を操作することで、サーバ内の機密ファイルなどが閲覧可能な状態になっています。ファイル名のみ指定できるようにするなどの対策が必要です。",
    $flawNames[11] => "リダイレクト先を任意のURLに指定できる状態になっており、フィッシングサイトへの誘導などに悪用される危険性があります。",
    $flawNames[12] => "HTTPレスポンスヘッダに改行コードを入力することで任意のヘッダを挿入できる状態になっており、セッションハイジャックなど様々な攻撃に繋がる恐れがあります。",
    $flawNames[13] => "レスポンスに不要なエラーメッセージが出力されています。設定ファイルなどを編集してエラー情報を隠すことを推奨します。",
    $flawNames[14] => "パラメータにCSRFトークンが存在しませんでした。重要な処理の場合はCSRFトークンを付与することを推奨します。",
    $flawNames[15] => "当該URLにDOM Based XSSの脆弱性が発見されました。外部からの入力でDOMを生成する箇所に適切なエスケープ処理を施す必要があります。",
    $flawNames[16] => "サーバ内部でエラーが発生しています。エラー内容によっては重大な脆弱性が存在している可能性があるので手動診断などを行うことを推奨します。"];

// 各脆弱性に対する対策方法を表示するための配列
$solution = [$flawNames[0] => "下記コードのようにhtmlspecialcharsメソッドを使いエスケープ処理を行う。もしくは「<」などの特殊文字を「&lt」などに直接置き換えをするなどが挙げられます。",
             $flawNames[1] => "下記コードのようにプレースホルダを使用してSQL文を組み立てることで攻撃を防ぐことができます。",
             $flawNames[2] => "当該ページのソースコードに下記コードを追加してヘッダーを付与することで対策が可能です。また、ページごとに付与することが困難な場合は「.htaccess」または「httpd.conf」ファイルに「Header set X-FRAME-OPTIONS \"DENY\"」を記述することでも対策が可能です。",
             $flawNames[3] => "当該ページのソースコードに下記コードを追加してヘッダーを付与することで対策が可能です。また、ページごとに付与することが困難な場合は「.htaccess」または「httpd.conf」ファイルに「Header set Content-Security-Policy 各種設定」を記述することでも対策が可能です。(各種設定については「https://developer.mozilla.org/ja/docs/Web/HTTP/CSP」をご参照ください)",
             $flawNames[4] => "当該ページのソースコードに下記コードを追加してSecure属性を付与することで対策が可能です。もしくは、「.htaccess」または「httpd.conf」ファイルに「php_flag session.cookie_secure On」を記述することでも対策が可能です。",
             $flawNames[5] => "当該ページのソースコードに下記コードを追加してHttpOnly属性を付与することで対策が可能です。もしくは、「.htaccess」または「httpd.conf」ファイルに「session.cookie_httponly = On」を記述することでも対策が可能です。",
             $flawNames[6] => "「httpd.conf」ファイルの「ServerTokens オプション」のオプション部分をProdに変更することでApacheのバージョン情報を非表示にすることができます。",
             $flawNames[7] => "HTTPS化を行うにはそれぞれ環境ごとに様々な方法がありますので、ご自身の環境にあった方法で実装していただければと思います。",
             $flawNames[8] => "当該ディレクトリにindexファイルを設置することで、外部からディレクトリ構造を隠ぺいすることができます。",
             $flawNames[9] => "open()やsystem()などの外部プログラムを呼び出し可能な関数を極力使用しないことや、あらかじめ許可された文字列のみ受け付けることで対策が可能です。",
             $flawNames[10] => "外部からのパラメータでファイル名を直接指定する実装を避ける。または、下記コードのように固定のディレクトリを指定し、かつファイル名にディレクトリ名が含まれないようにすることで対策が可能です。",
             $flawNames[11] => "リダイレクト先をあらかじめ定めたパスにしか移動できないようプログラムを変更することで対策が可能です。",
             $flawNames[12] => "%0dや%0aなどの改行コードのエスケープ処理やユーザからの入力をレスポンスヘッダに使用しないようにすることで、対策が可能です。",
             $flawNames[13] => "php.iniファイルにあるdisplay_errorsをoffにすることでPHPで発生するエラーメッセージを非表示にすることができます。",
             $flawNames[14] => "CSRFトークンを作成してリクエストが本人のものかどうかを確認することや、CookieにSame-Site属性のLaxまたはStrictを付与することで対策が可能です。",
             $flawNames[15] => "下記コードのように入力された値を文字列として出力することで攻撃を防ぐことができます。",
             $flawNames[16] => "コードレビューやphp.iniファイルのdisplay_errorsをoffにするなどしてエラー内容を調べることができます。"];

// 対策方法に対する具体的なコードを表示するための配列
$solutioncode = [$flawNames[0] => "<?php\n\$text = htmlspecialchars(\$_POST['text'], ENT_QUOTES);\n?>",
                 $flawNames[1] => "<?php\n\$sql = \"SELECT * FROM user WHERE id = :id\"\n\$stmt = \$pdo->prepare(\$sql);\n\$stmt->bindValue(':id', \$id, PDO::PARAM_STR);\n\$stmt->execute();\n?>",
                 $flawNames[2] => "<?php header(\"X-FRAME-OPTIONS: DENY\"); ?>",
                 $flawNames[3] => "<?php header(\"Content-Security-Policy: 各種設定\");?>",
                 $flawNames[4] => "<?php\nini_set('session.cookie_secure', 1);\n//またはCookie作成時に付与\nsetcookie('cookie_name', 'cookie_value', ['path' => '/','secure' => true,]);\n?>",
                 $flawNames[5] => "<?php\nini_set('session.cookie_httponly', 1);\n//またはCookie作成時に付与\nsetcookie('cookie_name', 'cookie_value', ['path' => '/','httponly' => true,]);\n?>",
                 $flawNames[10] => "<?php\ndirname = '固定のディレクトリ名';\nfilename = \$_POST['filename'];\nfopen(dirname+basename(filename));\n?>",
                 $flawNames[13] => "display_errors = Off",
                 $flawNames[15] => "<script>\nelement.textContent = 入力値;\n</script>"];

if(isset($_GET['scanid'])){
    $check = $db->prepare("SELECT COUNT(*) AS cnt FROM scandata WHERE scanid=?");
    $check->execute(array($_GET['scanid']));
    $check = $check->fetch();
    if($check['cnt'] <= 0){
        header('Location: ./index.php');
        exit;
    }
    $attacknames = $db->prepare("SELECT attackname, COUNT(attackname) AS cnt FROM scanalertdata WHERE scanid=? GROUP BY attackname ORDER BY attackname");
    $attacknames->execute(array($_GET['scanid']));
}else{
    if($check['cnt'] <= 0){
        header('Location: ./index.php');
        exit;
    }
}

if(isset($_GET['attackname']) && isset($_GET['formnum'])){
    $check = $db->prepare("SELECT COUNT(*) AS cnt FROM scanalertdata WHERE scanid=? AND attackname=? AND formnum=?");
    $check->execute(array($_GET['scanid'], $_GET['attackname'], $_GET['formnum']));
    $check = $check->fetch();
    if($check['cnt'] <= 0){
        header('Location: ./index.php');
        exit;
    }
    $maindata = $db->prepare("SELECT * FROM scanalertdata WHERE scanid=? AND attackname=? AND formnum=?");
    $maindata->execute(array($_GET['scanid'], $_GET['attackname'], $_GET['formnum']));
    $maindata = $maindata->fetch();
}else{
    $check = $db->prepare("SELECT COUNT(*) AS cnt FROM scanalertdata WHERE scanid=?");
    $check->execute(array($_GET['scanid']));
    $check = $check->fetch();
    if($check['cnt'] <= 0){
        header('Location: ./AlertNotFound.php');
        exit;
    }
    $maindata = $db->prepare("SELECT * FROM scanalertdata WHERE scanid=? ORDER BY attackname");
    $maindata->execute(array($_GET['scanid']));
    $maindata = $maindata->fetch();
    header('Location: ./ViewScanData.php?scanid='. $_GET['scanid']. '&attackname='. $maindata['attackname']. '&boxnum=0'. '&risk='. $maindata['risk']. '&formnum='. $maindata['formnum']);
    exit;
}

function h($values){
    return htmlspecialchars($values, ENT_QUOTES);
}
?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <link rel="icon" href="../favicons/favicon.ico">
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../hanbagu.css">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@8"></script>
    <link rel ="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
    <link rel="stylesheet" href="./CSS/viewscandata.css">

    <!-- コードを綺麗に表示するためのライブラリ(シンタックスハイライト) 参考: https://qiita.com/taqumo/items/825c862517ba9d8567a1 -->
    <link rel="stylesheet" href="../PrismLibrary/prism.css">
    <script src="../PrismLibrary/prism.js" defer></script>

    <title>診断情報</title>
</head>
<body>
    <h1 id="title">診断結果</h1>
    <div id="optionbox"></div>
    <div id="flexbox">
    <a id="arrowbutton" href="./index.php"><i class="fa-solid fa-arrow-left"></i></a>
        <div class="mainviewbox">
            <div id="stage" style="width: 30%;height:450px;"></div>
            <div class="maininformation">
                <span class="mainmotourl headline">リクエスト元URL<br> <span class="maintext"><?php echo h($maindata['motourl']);?></span></span>
                <span class="mainurl headline">リクエスト先URL<br> <span class="maintext"><?php echo h($maindata['url']);?></span></span>
                <span class="mainattackname headline">脆弱性<br> <span class="maintext"><?php echo h($maindata['attackname']);?></span></span>
                <span class="mainrisk headline">危険度<br> <span class="maintext" style="color: <?php echo h($colors[$maindata['risk']]);?>; border-color: black;"><?php echo h($maindata['risk']);?></span></span>
                <span class="mainmethod headline">メソッド<br> <span class="maintext"><?php echo h($maindata['method']);?></span></span>
                <span class="mainparameter headline">パラメータ<br>
                
                <div class="parameterbox">
                    <div class="parametersubbox">
                        <span class="parameteritemkey">名前</span>
                        <span class="parameteritemval">値</span>
                    </div>
                    <?php
                    $parameters = json_decode($maindata['parameter'], true);
                    ?>
                    <?php if(isset($parameters)):?>
                        <?php foreach(array_keys($parameters) as $key):?>
                            <div class="parametersubbox">
                                <span class="parameteritemkey"><?php echo h($key);?></span>
                                <span class="parameteritemval"><?php echo h($parameters[$key]);?></span>
                            </div>
                        <?php endforeach;?>
                    <?php endif;?>
                </div>
                
                <span class="mainsetumei headline">概要:<br> <?php echo h($message[$maindata['attackname']]);?></span><br>
                
                <pre class="line-numbers"><code class="language-html"><?php echo h($maindata['errortext']);?></code></pre>
                <?php if(!empty($maindata['imgpath'])):?>
                    <a style="margin-bottom: 20px;display: inline-block;" href="javascript: $('#imgaTag').toggleClass('imgoff')">スクリーンショットを表示する>></a><br>
                    <a id="imgaTag" class="imgoff" href="<?php echo h($maindata['imgpath']);?>"><img id="img" src="<?php echo h($maindata['imgpath']);?>"></a><br>
                <?php endif;?>
                <span class="mainsolution headline">対策方法:<br> <?php echo h($solution[$maindata['attackname']]);?></span>
                <?php if(array_key_exists($maindata['attackname'], $solutioncode)):?>
                    <?php if($maindata['attackname'] == "DOM Based XSS"):?>
                        <pre class="line-numbers"><code class="language-html"><?php echo h($solutioncode[$maindata['attackname']]);?></code></pre>
                    <?php else:?>
                        <pre class="line-numbers"><code class="language-php"><?php echo h($solutioncode[$maindata['attackname']]);?></code></pre>
                    <?php endif;?>
                <?php endif;?>
            </div>
        </div>
        <div class="subviewbox">
            <?php
            $cnt = 0;
            ?>
            <ul class="include-accordion scroll-control">
                <?php foreach($attacknames as $attackname):?>
                    <li>
                        <button class="accordionBtn" type="button"><?php echo $attackname['attackname'];?>: (<?php echo $attackname['cnt'];?>件)</button>
                        <ul>
                            <?php
                            $query = $db->prepare("SELECT * FROM scanalertdata WHERE scanid=? AND attackname=?");
                            $query->execute(array($_GET['scanid'], $attackname['attackname']));
                            ?>
                            <?php foreach($query as $index):?>
                                <li>
                                    <div class="subviewitem" id="<?php echo 'box'. $cnt;?>" onclick="itemchange(<?php echo $cnt;?>, <?php echo h($index['scanid']);?>, '<?php echo h($index['attackname']);?>', '<?php echo h($index['risk']);?>', <?php echo h($index['formnum']);?>)">
                                        <span class="attackname"><?php echo $index['attackname'];?></span><br>
                                        <span class="url"><?php echo h($index['url']);?></span>
                                        <span class="scanid" style="display: none"><?php echo $index['scanid'];?></span>
                                    </div>
                                </li>
                                <?php $cnt++;?>
                            <?php endforeach;?>
                        </ul>
                    </li>
                <?php endforeach;?>
            </ul>
        </div>
    </div>
    
    <script src="../jquery-3.5.1.min.js"></script>
    <script src="
https://cdn.jsdelivr.net/npm/echarts@5.4.1/dist/echarts.min.js
"></script>
    <script src="./JS/ViewScanData.js"></script>
</body>
</html>