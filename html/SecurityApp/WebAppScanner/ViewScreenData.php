<?php
require("../DBconnect.php");

if(!empty($_GET['scanid'])){
    $check = $db->prepare("SELECT COUNT(*) AS cnt FROM scandata WHERE scanid=?");
    $check->execute(array($_GET['scanid']));
    $check = $check->fetch();
    if($check['cnt'] <= 0){
        header('Location: index.php');
        exit;
    }
    // DBからURLごとリスクごとの検出数を取得する
    $query = $db->prepare("SELECT url, risk, COUNT(risk) AS riskcnt, COUNT(*) as cnt FROM scanalertdata WHERE scanid=? GROUP BY url, risk");
    $query->execute(array($_GET['scanid']));
    $kekka_array = [];
    foreach($query as $index){
        $tmp = ['url' => $index['url'], 'risk' => $index['risk'], 'riskcnt' => $index['riskcnt'], 'cnt' => $index['cnt']];
        array_push($kekka_array, $tmp);
    }
    // ページにタイトルがある場合はURLをタイトルに置き換える
    $getpagetitle = $db->prepare("SELECT * FROM screendata WHERE scanid=?");
    $getpagetitle->execute(array($_GET['scanid']));
    $tmp2 = $kekka_array;
    foreach($getpagetitle as $index){
        $cnt = 0;
        foreach($kekka_array as $index2){
            if($index['pageurl'] == $index2['url']){
                $tmp2[$cnt]['url'] = $index['pagetitle'];
            }
            $cnt++;
        }
    }
    $kekka_array = $tmp2;

    $viewdata = $db->prepare("SELECT * FROM screendata WHERE scanid=?");
    $viewdata->execute(array($_GET['scanid']));
}else{
    header('Location: index.php');
    exit;
}

function escape($value){
    return htmlspecialchars($value, ENT_QUOTES);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="icon" href="../favicons/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="./CSS/viewscreendata.css">
    <title>巡回結果画面</title>
</head>
<body>
    <div id="stage"></div>
    <!-- ページごとの検出数の棒グラフを画面上部に表示して、下部には巡回した画面一覧をスクショで表示する 参考画像: https://d1tlzifd8jdoy4.cloudfront.net/wp-content/uploads/2022/04/ss-2022-04-27-18.59.10.png -->
    <div id="datatag" data-array="<?php echo escape(json_encode($kekka_array));?>"></div>
    <div class="ViewScreenBox">
        <h1 id="screenboxtitle">画面一覧</h1>
        <div class="flexbox">
            <?php foreach($viewdata as $index):?>
                <div class="ViewScreenSubBox">
                    <a href="<?php echo escape(str_replace("../", "./Python/", $index['imgpath']));?>" target="_blank">
                        <img class="viewscreenimg" src="<?php echo escape(str_replace("../", "./Python/", $index['imgpath']));?>" alt="">
                    </a><br>
                    <span class="pageurl"><?php echo escape($index['pagetitle']);?></span>
                </div>
            <?php endforeach;?>
        </div>
    </div>
    <script src="
https://cdn.jsdelivr.net/npm/echarts@5.4.1/dist/echarts.min.js
"></script>
    <script src="../jquery-3.5.1.min.js"></script>
    <script src="./JS/ViewScreenData.js"></script>
</body>
</html>