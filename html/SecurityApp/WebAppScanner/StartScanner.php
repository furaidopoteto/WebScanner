<?php
require("../DBconnect.php");
if(!empty($_POST)){
    $command="python3 ./Python/Diagnosis.py ". escapeshellarg($_POST['url']). " ". escapeshellarg($_POST['autopatrol']). " ". escapeshellarg($_POST['advancedmode']);
    exec($command,$output);
    $json = json_encode(["res" => $output]);
    echo $json;
}
?>