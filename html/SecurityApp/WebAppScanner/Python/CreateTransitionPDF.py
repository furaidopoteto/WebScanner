import graphviz
import uuid
import datetime
import html
import os
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Crawler import Login


# 受け取った連想配列から画面遷移図を作成する関数
def create_graph(associative_array, pdfimages, ORIGIN, SCANID, ScreenTitle):
    # rankdirは遷移図のデザインでLRは左から右に遷移していく、nodesepとranksepはノード間またはエッジ間の間隔を指定する
    graph = graphviz.Digraph(format='pdf', graph_attr={'rankdir': 'LR', 'nodesep': '3', 'ranksep': '3'})

    # ノードとエッジの追加
    # penwidthはエッジの太さ、arrowsizeは矢印の大きさ
    for source_node, target_nodes in associative_array.items():
        if isinstance(target_nodes, list):
            target_nodes = list(dict.fromkeys(target_nodes))
            for target_node in target_nodes:
                graph.edge(source_node, target_node, _attributes={'penwidth': '10', 'arrowsize': '5'})
        else:
            graph.edge(source_node, target_nodes, _attributes={'penwidth': '10', 'arrowsize': '5'})

    # 画像の追加
    for key in pdfimages.keys():
        Title = str(html.escape(ScreenTitle[key])).replace("\\", "")
        imagepath = str(html.escape(pdfimages[key])).replace("\\", "")
        if(len(ScreenTitle[key]) <= 0):
            Title = "No Title"
        # href属性はエスケープ処理しないとエラーが発生する 参考: https://docs.python.org/3/library/html.html#html.escape
        graph.node(str(key).replace(ORIGIN, ""), shape="record", label=f"""<<table style="rounded">
       <tr><td border="0"><font point-size="100">{Title}</font></td></tr>
       <hr/>
       <tr><td border="0"><img src="{imagepath}" /></td></tr>
       </table>>""")
    
    pdffilepath = './Python/PDFFiles/'+str(SCANID)+'_transition_diagram'
    # 画面遷移図の保存
    graph.render(pdffilepath)# badtodoアプリに対しての画面遷移図を生成しようとするとエラーが発生する問題に対処する必要がある。
    return pdffilepath+".pdf"


def create_transition_img(associative_array, ORIGIN, loginurl, loginpara, SCANID, scanonly, pdfimages, fasturl, ScreenTitle):
    # 一番最初のURLはクローラ側でスクショを撮影していないので撮影する
    if(fasturl not in pdfimages):
        # chromedriverの設定
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
        # ウィンドウのサイズを最大化する
        w = 1500
        h = 1000
        driver.set_window_size(w, h)
        
        start_time = datetime.datetime.now()
        driver = Login(loginurl, driver, loginpara, start_time, ORIGIN)
        driver.get(fasturl)
        
        filepath = "./Python/TransitionImages/"+str(SCANID)+"/"+str(uuid.uuid4())+".png"
        # Get Screen Shot
        driver.save_screenshot(filepath)
        
        pdfimages[fasturl] = filepath.replace("./Python/", "../")
        ScreenTitle[fasturl] = driver.title
        # ドライバーのメモリ解法
        driver.quit()
    
    
    # 配列の重複した値の削除 参考: https://office54.net/python/data-types/list-duplicate-remove#section2
    for key in associative_array.keys():
        tmpdict = dict.fromkeys(associative_array[key])
        associative_array[key] = list(tmpdict)
    
    # print(associative_array)
    
    try:
        os.mkdir("./Python/TransitionImages/"+str(SCANID))
    except FileExistsError:
        pass
    
    # 巡回ページの連想配列と撮影したスクショをもとに画面遷移図を作成する
    pdffilepath = create_graph(associative_array, pdfimages, ORIGIN, SCANID, ScreenTitle)
    
    # scanonlyがTrueの場合は画面遷移図のzipファイルを作成して、元のファイル群は削除する
    if(scanonly):
        # 画像とPDFファイルをzipにまとめる
        with zipfile.ZipFile('./Python/ZipPDFFiles/transition_diagram.zip', 'w') as zipf:
            zipf.write(pdffilepath)
            for image_file in pdfimages.values():
                zipf.write(str(image_file).replace("../", "./Python/"))


        # 不要なファイルを削除
        os.remove(pdffilepath)
        os.remove(pdffilepath.replace(".pdf", ""))
        for image_file in pdfimages.values():
            os.remove(str(image_file).replace("../", "./Python/"))
        pdffilepath = "./Python/ZipPDFFiles/transition_diagram.zip"

    return pdffilepath
