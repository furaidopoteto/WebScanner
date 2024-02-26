<?php
require("../DBconnect.php");

// ajaxで連想配列を送る 参考: https://mgmgblog.com/post-3226/
// parse_strでクエリーストリング形式から連想配列に変換する 参考: https://suin.io/526
$query = file_get_contents('php://input');
parse_str($query, $queryarray);
$loginparameter = $queryarray['loginparameter'];
$manualurls = $queryarray['manualurls'];
$csrftokens = $queryarray['csrftokens'];
$sessids = $queryarray['sessids'];
if(!empty($queryarray)){
    $insert = $db->prepare("UPDATE scannersetting SET manualurls_json=?, loginpara_json=?, loginurl=?, method=?, sessids_json=?, csrftokens_json=?, loginflagstr=?, loginflagpage=?, time=NOW()");
    $insert->execute(array($manualurls, $loginparameter, $queryarray['loginurl'], $queryarray['loginmethod'], $sessids, $csrftokens, $queryarray['loginflagstr'], $queryarray['loginflagpage']));
    echo json_encode("success");
    exit;
}
?>