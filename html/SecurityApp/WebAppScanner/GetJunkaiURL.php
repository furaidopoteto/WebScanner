<?php
require("../DBconnect.php");

if(!empty($_POST)){
    $command="python3 ./Python/GetURLs.py ". escapeshellarg($_POST['url']);
    
    exec($command,$output);
    $json = json_encode(["res" => $output]);
    echo $json;
}
?>