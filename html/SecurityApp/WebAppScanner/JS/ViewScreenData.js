'use strict';

const myChart = echarts.init(document.getElementById('stage'));
const datatag = document.getElementById('datatag');
const TEMPRISK = ["Info", "Low", "Medium", "High", "Critical"];

// htmlのdata属性を使いDBから受け取ったデータをJavaScriptで受け取る 参考: https://web-camp.io/magazine/archives/78352
let graphdata = JSON.parse(datatag.dataset.array);

// ページURLとページ別リスク別検出数を格納した変数を用意する
let urls = [];
let pagerisk = {};

for(let i = 0;i<graphdata.length;i++){
  urls.push(graphdata[i]['url']);
  let riskname = String(graphdata[i]['risk']);
  // JavaScriptは連想配列でキーに変数を指定する場合は[]で囲む必要がある 参考: https://codelab.website/javascript-dictionary-key-variable/
  // JavaScriptで連想配列をマージする場合はObject.assign()を使用する 参考: https://zenn.dev/kou_pg_0131/articles/js-merge-multiple-objects
  if(pagerisk[graphdata[i]['url']] == undefined){
    pagerisk[graphdata[i]['url']] = {}
  }
  Object.assign(pagerisk[graphdata[i]['url']], {[riskname]: graphdata[i]['riskcnt']});
}
// リスクごとの検出数をページごとの順番で格納していく
let riskcnt = {};
for(let key of Object.keys(pagerisk)){
  for(let rn of TEMPRISK){
    if(riskcnt[rn] == undefined){
      riskcnt[rn] = [];
    }
    if(!(rn in pagerisk[key])){
      Object.assign(pagerisk[key], {[rn]: null})
    }
    riskcnt[rn].push(pagerisk[key][rn])
  }
}

const option = {
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      // Use axis to trigger tooltip
      type: 'shadow' // 'shadow' as default; can also be 'line' or 'shadow'
    }
  },
  legend: {},
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value'
  },
  yAxis: {
    type: 'category',
    data: Object.keys(pagerisk)
  },
  series: [
    {
      name: TEMPRISK[0],
      type: 'bar',
      stack: 'total',
      color: "gray",
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: riskcnt[TEMPRISK[0]]
    },
    {
      name: TEMPRISK[1],
      type: 'bar',
      stack: 'total',
      color: '#0055ff',
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: riskcnt[TEMPRISK[1]]
    },
    {
      name: TEMPRISK[2],
      type: 'bar',
      stack: 'total',
      color: 'orange',
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: riskcnt[TEMPRISK[2]]
    },
    {
      name: TEMPRISK[3],
      type: 'bar',
      stack: 'total',
      color: 'red',
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: riskcnt[TEMPRISK[3]]
    },
    {
      name: TEMPRISK[4],
      type: 'bar',
      stack: 'total',
      color: '#ad0202',
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: riskcnt[TEMPRISK[4]]
    }
  ]
};


myChart.setOption(option);