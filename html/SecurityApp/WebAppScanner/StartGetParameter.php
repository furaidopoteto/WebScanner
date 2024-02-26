<?php

if(!empty($_POST)){
    $command="python3 ./Python/GetParameter.py ". escapeshellarg($_POST['url']);
    exec($command,$output);
    $json = json_encode($output);
    echo $json;
}
?>