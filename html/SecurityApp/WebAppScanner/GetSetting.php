<?php
require("../DBconnect.php");

if(!empty($_POST)){
    $query = $db->query("SELECT * FROM scannersetting");
    $query = $query->fetch();
    $json = json_encode($query);
    echo $json;
}
?>