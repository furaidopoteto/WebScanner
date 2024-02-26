<?php
require("../DBconnect.php");

if(!empty($_POST)){
    $query = $db->query("SELECT * FROM attackinfo");
    $query = $query->fetch();
    $datas = ["infotitle" => $query['infotitle'], "domain" => $query['domain'], "parameter" => $query['parameter'], "nowcnt" => $query['nowcnt'],
              "sumcnt" => $query['sumcnt'], "percent" => $query['percent'], "alertcnt" => $query['alertcnt'], "json_urls" => $query['json_urls'],
              "sum_pages" => $query['sum_pages'], "now_page_cnt" => $query['now_page_cnt']];
    $json = json_encode($datas);
    echo $json;
}
?>