<?php
try{
    $db = new PDO("mysql:dbname=secapp;host=mysql;charset=utf8", 'root', 'furenntifuraizu');
}catch(PDOException $e){
    $e->getMessage();
}
?>