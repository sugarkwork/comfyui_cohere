# comfyui_cohere

ComfyUI から cohere （Command R+）を使用するためのノードです。


ComfyUI の起動 bat ファイルを編集して、以下のように Cohere から取得した API キーを記述する必要があります。

    @echo off
    set COHERE_API_KEY=COHERE_API_KEY
    .\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build
    pause

