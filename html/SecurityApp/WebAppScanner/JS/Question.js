'use strict';

const question = document.getElementById("question");

question.addEventListener("click", function(){
    Swal.fire({
        title: 'ヘルプ',
        html: `<h1><a style="font-size: 25px;" href="javascript:viewattacks();">検出可能な脆弱性一覧</a></h1>
               <h1><a style="font-size: 25px;" href="javascript:helpadvanced();">高度な巡回機能について</a></h1>`
        }).then(function(result) {
            
        });
})

function viewattacks(){
    Swal.fire({
        title: '検出可能な脆弱性一覧',
        width: 600,
        html: `<div style="width: 500px; text-align: left; padding-left: 100px; font-size: 20px;">
                  <ul>
                    <li>XSS</li>
                    <li>DOM Based XSS</li>
                    <li>SQLインジェクション(ブラインドも可)</li>
                    <li>OSコマンドインジェクション(ブラインドも可)</li>
                    <li>ディレクトリトラバーサル</li>
                    <li>ディレクトリリスティング</li>
                    <li>オープンリダイレクト</li>
                    <li>HTTPヘッダインジェクション</li>
                    <li>バージョン情報の漏洩</li>
                    <li>不要なエラーメッセージの出力</li>
                    <li>HTTPS通信の有無</li>
                    <li>CSRFトークンの有無</li>
                    <li>Secure属性の有無</li>
                    <li>HttpOnly属性の有無</li>
                    <li>Content-Security-Policyヘッダの有無</li>
                    <li>X-Frame-Optionsヘッダの有無</li>
                    <li>HTTPステータスコード500-内部エラー</li>
                  </ur>
                </div>
               `
        }).then(function(result) {
            
        });
}

function helpadvanced(){
  Swal.fire({
    title: '高度な巡回についての説明',
    width: 1500,
    html: `<div style="text-align: left; padding-left: 100px; font-size: 20px;">
              <ul>
                <li>診断対象サイトのドメイン名またはIPアドレスを入力しブラウザ起動ボタンをクリック</li>
                <img class="helpimages" src="./JS/QuestionImages/helpadvanced1.png">
                <li>「ブラウザへアクセス」をクリックし、パスワード「secret」で接続</li>
                <img class="helpimages" src="./JS/QuestionImages/helpadvanced2.png">
                <li>画面上部のURLバーから診断対象サイトへ移動</li>
                <img class="helpimages" src="./JS/QuestionImages/helpadvanced3.png">
                <li>診断したいページへアクセスしたりサイトを操作する</li>
                <img class="helpimages" src="./JS/QuestionImages/helpadvanced4.png">
                <li>すると行った操作で発生したリクエストを取得できます</li>
                <img class="helpimages" src="./JS/QuestionImages/helpadvanced5.png">
                <li>停止した状態でURLをクリックするとリクエストの詳細情報が表示されます</li>
                <img class="helpimages" src="./JS/QuestionImages/helpadvanced6.png">
                <li>メイン画面に戻り高度な巡回というチェックボックスをオンにして診断を開始します<br>※ログインが必要なページの場合はログイン情報も設定してください</li>
                <img class="helpimages" src="./JS/QuestionImages/helpadvanced7.png">
              </ur>
            </div>
           `
    }).then(function(result) {
        
    });
}