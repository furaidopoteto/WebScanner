<?php
try{
    $data = new PDO("mysql:dbname=yoyakudb3;host=mysql;charset=utf8", 'root', 'furenntifuraizu');
}catch(PDOException $e){
    echo $e->getMessage();
}
?>