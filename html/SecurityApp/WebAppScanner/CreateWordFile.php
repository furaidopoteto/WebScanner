<?php

if(!empty($_POST)){
    $command="python3 ./Python/CreateWordFile.py ". escapeshellarg($_POST['scanid']);
    exec($command,$output);
    $json = json_encode($output);
    echo $json;
}
?>