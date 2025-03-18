# 資料結構

 - 授課教師：蔡芸琤老師
 - 姓名：邱鈺婷
 - 系級：科技系116

# 作業繳交區


# HW
尋找與確認要研究的方向，完成對程式碼部分的資料抽換及問題抽換，並製作架構圖(流程圖)

  ## Youbike探查器(試做版) 
  
   嘗試從台北公開資料網站使用Youbike即時資料，特別觀察師大附近幾個特定站點，去判斷建不建議借youbike，以及提醒那些地點無車可借、無位可還。

   使用資料: 台北市 YouBike 2.0 API URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"

   程式碼參考: 
   - [youbikeAgent.py](https://github.com/MocuAcqu/1132Database/blob/main/youbikeAgent.py)、
   - [youbike_analysis_log.csv](https://github.com/MocuAcqu/1132Database/blob/main/youbike_analysis_log.csv)

   架構圖:
   ![image](https://github.com/MocuAcqu/1132Database/blob/main/Youbike%E6%8E%A2%E6%9F%A5%E5%99%A8.png)

   
  ## 虛擬導盲器 (方案一)
    
   因為希望製作更不一樣，並且能帶來不同意義的成果，想到導盲犬數量不足夠引導目前的盲人數量，希望製作一個能夠替代導盲犬提示盲者的虛擬導盲犬機器。

   (影像資料有點不易收集，因這次主題無提供影像設備，因此需考慮一下)
   ![image](https://github.com/MocuAcqu/1132Database/blob/main/%E8%99%9B%E6%93%AC%E5%B0%8E%E7%9B%B2%E5%99%A8.png)

- 預計使用的套件
- 相對應程式碼
  
  TextMentionTermination：設定對話的終止條件。
  RoundRobinGroupChat：管理 AI 代理人的對話方式（輪流回應）。
  OpenAIChatCompletionClient：連接 OpenAI API，使用 gemini-2.0-flash 模型來分析數據。


# 課程練習

## DRai
【親子對話分析專家】
假設身分為親子對話分析專家，去分析一段錄音逐字對話紀錄中，是否觸及評分項目的標記，並輸出成CSV檔。
- 使用資料: [113.csv](https://github.com/MocuAcqu/1132Database/blob/main/DRai/113.csv)
- 程式碼: [DRai.py]()
- 評分項目
  | 引導 | 評估(口語、跟讀的內容有關) | 評估(非口語、寶寶自發性動作、跟讀的內容有關) | 延伸討論 | 複述 | 開放式問題 | 填空 | 回想 | 人事時地物問句 | 連結生活經驗 | 備註 |
  |-|-|-|-|-|-|-|-|-|-|-|

【大學生面試對話分析專家】
假設身分為大學生面試對話分析專家，去分析一段錄音逐字對話紀錄中，是否觸及評分項目的標記，並輸出成CSV檔。(替換老師範例資料的成果)
- 使用資料: [interview.csv]()
- 程式碼: [DRai2.py]()
