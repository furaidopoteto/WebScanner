'use strict';

const mainviewbox = document.querySelector(".mainviewbox");
const subviewitems = document.querySelectorAll(".subviewitem");
const title = document.getElementById("title");
const optionbox = document.getElementById("optionbox");
const risks = ["Info", "Low", "Medium", "High", "Critical"];
const colors = {"Info": "gray", "Low": "#0055ff", "Medium": "orange", "High": "red", "Critical": "#ad0202"};

// URLを取得
let url = new URL(window.location.href);

// URLSearchParamsオブジェクトを取得
let params = url.searchParams;

const boxnum = params.get("boxnum");

const risk = params.get("risk");

subviewitems.forEach((e) => e.style.backgroundColor = "")
const subviewitem = subviewitems[boxnum];
subviewitems[boxnum].style.backgroundColor = "aqua";


window.addEventListener("load", function(){
    const mainattackname = subviewitem.querySelector(".attackname").textContent;

    // Initialize the echarts instance based on the prepared dom
    var myChart = echarts.init(document.getElementById("stage"));

    const riskval = {"Info": 1, "Low": 3, "Medium": 5, "High": 7, "Critical": 9}

    // Specify the configuration items and data for the chart 参考: https://stackblitz.com/edit/react-ffdjoy?file=src%2FApp.js
    var option = {
        title: {
            text: mainattackname,
            left: 'left',
        },
        series: [
        {
            type: 'gauge',
            startAngle: 180,
            endAngle: 0,
            min: 0,
            max: 10,
            progress: {
                show: false,
                width: 10,
            },
            data: [
            {
                value: riskval[risk],
                name: risk
            },
            ],
            axisLine: {
                roundCap: false,
                lineStyle: {
                    width: 40,
                    color: [
                    [0.2, colors["Info"]],
                    [0.4, colors["Low"]],
                    [0.6, colors["Medium"]],
                    [0.8, colors["High"]],
                    [1, colors["Critical"]]
                    ],
                },
            },
            axisTick: {
                show: false,
            },
            splitLine: {
                length: 15,
                lineStyle: {
                    width: 0,
                    color: '#999',
                },
            },
            axisLabel: {
                show: false,
            },
            pointer: {
                length: '85%'
            },
            anchor: {
                show: true,
                showAbove: true,
                size: 10,
                itemStyle: {
                    borderWidth: 3,
                },
            },
            detail: {
                show: false
            },
        },
        ],
    };

    // Display the chart using the configuration items and data just specified.
    myChart.setOption(option);

    // グラフを生成した後に選択されているboxのアコーディオンメニューをクリックして開かせる
    subviewitems[boxnum].parentElement.parentElement.previousElementSibling.click()
})

function itemchange(boxnum, scanid, attackname, risk, formnum){
    location.href = "./ViewScanData.php?boxnum="+boxnum+"&scanid="+scanid+"&attackname="+attackname+"&risk="+risk+"&formnum="+formnum;
}

const scanid2 = subviewitems[0].querySelector(".scanid").textContent;
$.ajax({
    type: "post",
    url: "./GetScanData.php",
    dataType: "json",
    data: {"scanid": scanid2, "getrisk": "yes"}
}).then(function(kekka){
    for(let i = 0;i<risks.length;i++){
        title.insertAdjacentHTML("beforeend", `<div class="riskbox"><span style="color: ${colors[risks[i]]}">${risks[i]}</span><br>${kekka[risks[i]]}</div>`)
    }
    // title.insertAdjacentHTML("beforeend", `<section><a style="margin-top: 20px;" class="optionbutton btn_03" href="javascript: pagefilter()">ページ絞り込み</a></section>`)
    optionbox.insertAdjacentHTML("beforeend", `<section><a class="optionbutton btn_03" href="javascript: viewsearchurls()">探索URL一覧</a></section><br>`)
    optionbox.insertAdjacentHTML("beforeend", `<section><a class="optionbutton btn_03" href="javascript: CreateWordFile()">レポート作成</a></section><br>`)
    optionbox.insertAdjacentHTML("beforeend", `<section><a class="optionbutton btn_03" target="_blank" href="./Python/PDFFiles/${scanid2}_transition_diagram.pdf">画面遷移図</a></section><br>`)
    optionbox.insertAdjacentHTML("beforeend", `<section><a class="optionbutton btn_03" target="_blank" href="./ViewScreenData.php?scanid=${scanid2}">巡回結果確認</a></section><br>`)
}).fail(function(errorThrown){
    console.log(errorThrown);
})

function viewsearchurls(){
  $.ajax({
    type: "post",
    url: "./GetScanData.php",
    dataType: "json",
    data: {"scanid": scanid2}
  }).then(function(kekka){
    let htmltext = `<div style="width: 100%; text-align: left; font-size: 20px;">`;
    for(let i = 0;i<kekka.length;i++){
      htmltext += `<h5>・${kekka[i]}</h5>`;
    }
    htmltext += `</div>`
    Swal.fire({
      title: '探索URL一覧',
      width: 1200,
      html: htmltext,
      showCancelButton: false,
      showConfirmButton: false
      }).then(function(result) {
          
      });  
  }).fail(function(errorThrown){
      console.log(errorThrown);
  })
}

// アコーディオンメニューのプログラム 参考: https://www.bring-flower.com/blog/accordion-menu/
// メニューを開く関数
const slideDown = (el) => {
    el.style.height = 'auto'; //いったんautoに
    let h = el.offsetHeight; //autoにした要素から高さを取得
    el.style.height = h + 'px';
    el.animate([ //高さ0から取得した高さまでのアニメーション
      { height: 0 },
      { height: h + 'px' }
    ], {
      duration: 300, //アニメーションの時間（ms）
     });
  };
  
  // メニューを閉じる関数
  const slideUp = (el) => {
    el.style.height = 0;
  };
  
  let activeIndex = null; //開いているアコーディオンのindex
  
  //アコーディオンコンテナ全てで実行
  const accordions = document.querySelectorAll('ul.include-accordion');
  accordions.forEach((accordion) => {
  
    //アコーディオンボタン全てで実行
    const accordionBtns = accordion.querySelectorAll('.accordionBtn');
    accordionBtns.forEach((accordionBtn, index) => {
      accordionBtn.addEventListener('click', (e) => {
        activeIndex = index; //クリックされたボタンを把握
        e.target.parentNode.classList.toggle('active'); //ボタンの親要素（=ul>li)にクラスを付与／削除
        const content = accordionBtn.nextElementSibling; //ボタンの次の要素（=ul>ul）
        if(e.target.parentNode.classList.contains('active')){
          slideDown(content); //クラス名がactive（＝閉じていた）なら上記で定義した開く関数を実行
        }else{
          slideUp(content); //クラス名にactiveがない（＝開いていた）なら上記で定義した閉じる関数を実行
        }
        accordionBtns.forEach((accordionBtn, index) => {
          if (activeIndex !== index) {
            accordionBtn.parentNode.classList.remove('active');
            const openedContent = accordionBtn.nextElementSibling;
            slideUp(openedContent); //現在開いている他のメニューを閉じる
          }
        });
        //スクロール制御のために上位階層ulのクラス名を変える
        let container = accordion.closest('.scroll-control'); //sroll-controlnのクラス名である親要素を取得
        if(accordionBtn.parentNode.classList.contains('active') == false && container !== null ){
          container.classList.remove('active')
        }else if (container !== null){
          container.classList.add('active')
        }
      });
    });
  });


// Wordファイルの報告書を作成するPHPプログラムを呼び出す関数
function CreateWordFile(){
  $.ajax({
    type: "post",
    url: "./CreateWordFile.php",
    dataType: "json",
    data: {"scanid": scanid2}
  }).done(function(kekka){
    let filename = JSON.parse(kekka[0]);
    var anchor = document.createElement('a');
    anchor.download = filename["filename"];
    anchor.href = filename["filename"];
    anchor.click();
  }).fail(function(kekka){
    console.log("ファイルの作成に失敗しました");
  })
}

/* ページを絞り込む処理を実装しようとしたがシンタックスハイライトを機能させるために情報の切り替えを
   非同期ではなく同期処理で実装していたので絞り込み機能の実装が難しくなった

let fastflag = true;
let fastalertcnt = [];
// チェックされているURLを保存しておく配列
let CheckedURL = [];
// スキャン結果をページごとに絞り込む処理を行う関数
function pagefilter(){
  let htmltext = ``;
  // ajax一発目で探索URL一覧を取得する
  $.ajax({
    type: "post",
    url: "http://127.0.0.1/MyPHP/Main3/originalcode/SecurityApp/WebAppScanner/GetScanData.php",
    dataType: "json",
    data: {"scanid": scanid2}
  }).then(function(kekka){
    // 二発目のajaxで探索URLに対するスクショやタイトルなどを取得する
    $.ajax({
      type: "post",
      url: "http://127.0.0.1/MyPHP/Main3/originalcode/SecurityApp/WebAppScanner/GetScanData.php",
      dataType: "json",
      data: {"scanid": scanid2, "urls": JSON.stringify(kekka)}
    }).then(async function(kekka2){
      const URLS = kekka;
      const IMGANDURL = kekka2;
      // 表示順にURLを格納する配列
      let ViewURL = [];
      let cnt = 0
      let checkflag = "";
      // スクショが存在する場合はページ絞り込み画面にスクショとタイトルを表示する
      for(let key in IMGANDURL){
        if(CheckedURL.indexOf(key) >= 0){
          checkflag = "checked";
        }else{
          checkflag = "";
        }
        const imagepath = `${IMGANDURL[key][0]}`.replace("../", "./Python/");
        htmltext += `<div class="form-check">
                      <label class="form-check-label" for="checkbox${cnt}">
                        <img class="pageimg" src="${imagepath}"><br>
                        <input class="form-check-input" type="checkbox" value="" id="checkbox${cnt}" ${checkflag}>
                        ${IMGANDURL[key][1]}
                      </label>
                    </div>`;
        cnt++;
        ViewURL.push(key);
      }
      // それ以外のURLはそのまま表示する
      for(let i = 0;i<URLS.length;i++){
        if(IMGANDURL[URLS[i]] == undefined){
          if(CheckedURL.indexOf(URLS[i]) >= 0){
            checkflag = "checked";
          }else{
            checkflag = "";
          }
          htmltext += `<br><div class="form-check">
                        <label class="form-check-label" for="checkbox${cnt}" style="display: flex;">
                        <input class="form-check-input" type="checkbox" value="" id="checkbox${cnt}" ${checkflag}>
                        ${escape(URLS[i])}
                        </label>
                     </div>`;
          cnt++;
          ViewURL.push(URLS[i]);
        }
      }
      // ポップアップに対するイベントリスナーなどの設定を行う
      const { value: accept } = await Swal.fire({
        title: 'ページ絞り込み',
        html: htmltext,
        focusConfirm: false,
        width: 1900,
        showCancelButton: false, // There won't be any cancel button
        showConfirmButton: true, // There won't be any confirm button
      }).then(function(result){
        // チェック状態をリセット
        CheckedURL = [];
        // ポップアップを閉じたときに画面の表示内容を変更する処理を行う
        const subviewurls = document.querySelectorAll(".url");
        // 表示状態をリセット
        for(let i = 0;i<subviewurls.length;i++){
          subviewurls[i].parentElement.style.display = "";
          if(fastflag){
            // 初回の処理で元々の検出数を取得して配列に格納する
            const buttonelement = subviewurls[i].parentElement.parentElement.parentElement.parentElement.firstElementChild;
            let buttontext = buttonelement.textContent;
            const regex = /[^0-9]/g;
            const number = buttontext.replace(regex, "");
            fastalertcnt.push(number);
          }
          // 検出数を格納した配列を使用して表示状態をリセットする
          const buttonelement = subviewurls[i].parentElement.parentElement.parentElement.parentElement.firstElementChild;
          let buttontext = buttonelement.textContent;
          const regex = /[^0-9]/g;
          const number = buttontext.replace(regex, "");
          buttontext = buttontext.replace(number, fastalertcnt[i]);
          buttonelement.textContent = buttontext;
        }
        fastflag = false;
        // チェックが付いているページ以外の表示を削除する処理を行う
        for(let i = 0;i<cnt;i++){
          if(!document.getElementById(`checkbox${i}`).checked){
            for(let j = 0;j<subviewurls.length;j++){
              if(subviewurls[j].textContent == ViewURL[i]){
                // 絞り込みで選択されていない要素を画面から消す処理
                subviewurls[j].parentElement.style.display = "none";
                // 親要素から検出数を取得して数値を置き換える処理
                const buttonelement = subviewurls[j].parentElement.parentElement.parentElement.parentElement.firstElementChild;
                let buttontext = buttonelement.textContent;
                const regex = /[^0-9]/g;
                const number = buttontext.replace(regex, "");
                buttontext = buttontext.replace(number, number-1);
                buttonelement.textContent = buttontext;
              }
            }
          }else{
            // チェックが付いているURLをCheckedURL配列に追加する 
            CheckedURL.push(ViewURL[i]);
          }
        }
      }).fail(function(result){

      })
      
    }).fail(function(errorThrown2){
      console.log("スクリーンデータの取得に失敗しました");
    })
  }).fail(function(errorThrown){
    console.log(errorThrown);
  })
}
*/