<?php
session_start();
setcookie('name', null, time()-3600);//期限をマイナスにすればすぐに削除される
setcookie('pw', null, time()-3600);
$_SESSION = array();
session_destroy();
header('Location: home.php');
exit;
?>