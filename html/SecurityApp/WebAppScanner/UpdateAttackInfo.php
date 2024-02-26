<?php
require("../DBconnect.php");

if(!empty($_POST)){
    if(!empty($_POST['json_urls'])){
        $update = $db->prepare("UPDATE attackinfo SET infotitle=?, domain=?, parameter=?, nowcnt=?, sumcnt=?, percent=?, alertcnt=?, json_urls=?, time=NOW()");
        $update->execute(array($_POST['infotitle'], $_POST['domain'], $_POST['parameter'], $_POST['nowcnt'],
                               $_POST['sumcnt'], $_POST['percent'], $_POST['alertcnt'], $_POST['json_urls']));
    }else if($_POST['json_urls'] == "reset"){
        $update = $db->prepare("UPDATE attackinfo SET infotitle=?, domain=?, parameter=?, nowcnt=?, sumcnt=?, percent=?, alertcnt=?, json_urls=?, sum_pages=?, now_page_cnt=?, time=NOW()");
        $update->execute(array($_POST['infotitle'], $_POST['domain'], $_POST['parameter'], $_POST['nowcnt'],
                               $_POST['sumcnt'], $_POST['percent'], $_POST['alertcnt'], "", 0, 0));
    }else{
        $update = $db->prepare("UPDATE attackinfo SET infotitle=?, domain=?, parameter=?, nowcnt=?, sumcnt=?, percent=?, alertcnt=?, time=NOW()");
        $update->execute(array($_POST['infotitle'], $_POST['domain'], $_POST['parameter'], $_POST['nowcnt'],
                               $_POST['sumcnt'], $_POST['percent'], $_POST['alertcnt']));
    }

    // 巡回中のページ数が送られてきた場合はその値も更新する
    if(isset($_POST['sum_pages']) && $_POST['json_urls'] != "reset"){
        if($_POST['sum_pages'] >= 0){
            $update = $db->prepare("UPDATE attackinfo SET infotitle=?, domain=?, parameter=?, nowcnt=?, sumcnt=?, percent=?, alertcnt=?, sum_pages=?, now_page_cnt=?, time=NOW()");
            $update->execute(array($_POST['infotitle'], $_POST['domain'], $_POST['parameter'], $_POST['nowcnt'],
                                $_POST['sumcnt'], $_POST['percent'], $_POST['alertcnt'], $_POST['sum_pages'], $_POST['now_page_cnt']));
        }
    }
}
?>