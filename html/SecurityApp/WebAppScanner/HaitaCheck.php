<?php
require("../DBconnect.php");

if(!empty($_POST['check'])){
    if($_POST['check'] == "yes"){
        $query = $db->query("SELECT * FROM haita");
        $query = $query->fetch();
        echo $query['state'];
    }else{
        $update = $db->prepare("UPDATE haita SET state='Ready'");
        $update->execute(array());
    }
}
if(!empty($_POST['state'])){
    if($_POST['state'] == "stop"){
        $update = $db->prepare("UPDATE haita SET state='NotReady'");
        $update->execute(array());
    }
}
?>