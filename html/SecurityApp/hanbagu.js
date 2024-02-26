'use strict';

let hangabubutton = document.getElementById('hanbagubutton');

hangabubutton.addEventListener("click", function(){
    $("body").toggleClass("open");
    $(".top").toggleClass("topopen");
    $(".center").toggleClass("centeropen");
    $(".bottom").toggleClass("bottomopen");
})