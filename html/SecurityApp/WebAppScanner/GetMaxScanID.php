<?php
require("../DBconnect.php");

if(!empty($_POST['getscanid'])){
    $maxscanid = $db->query("SELECT MAX(scanid) AS maxscanid FROM scandata");
    $maxscanid = $maxscanid->fetch();
    $json = json_encode($maxscanid);
    echo $json;
}
?>