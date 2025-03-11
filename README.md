# 資料結構

 - 授課教師：蔡芸琤老師
 - 姓名：邱鈺婷
 - 系級：科技系116

# 作業繳交區


## HW
尋找與確認要研究的方向，完成對程式碼部分的資料抽換及問題抽換，並製作架構圖(流程圖)
- 製作版本
  - Youbike探查器(試做版) 
  
   嘗試從台北公開資料網站使用Youbike即時資料，特別觀察師大附近幾個特定站點，去判斷建不建議借youbike，以及提醒那些地點無車可借、無位可還。

   使用資料: 台北市 YouBike 2.0 API URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"

   檔案參考: youbikeAgent.py、youbike_analysis_log.csv

   程式碼:
  - 引入函式庫
     1. os: 用來讀取環境變數，例如 API 金鑰。
     2. asyncio: 用於非同步處理，提高程式效率。
     3. pandas: 處理 YouBike API 回傳的 JSON 數據並轉換成 DataFrame。
     4. requests: 取得 YouBike API 的即時數據。
     5. dotenv: 用於讀取 .env 檔案中的環境變數。
     6. autogen_agentchat 和 autogen_ext: 與 AI 代理人相關的函式庫，負責自動對話與分析。
。
  <pre><code>
  import os
  import asyncio
  import pandas as pd
  import requests

  from dotenv import load_dotenv
  from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
  from autogen_agentchat.conditions import TextMentionTermination
  from autogen_agentchat.teams import RoundRobinGroupChat
  from autogen_agentchat.messages import TextMessage
  from autogen_ext.models.openai import OpenAIChatCompletionClient
  </code></pre>

- 引入函式庫
     1. os: 用來讀取環境變數，例如 API 金鑰。
     2. asyncio: 用於非同步處理，提高程式效率。
     3. pandas: 處理 YouBike API 回傳的 JSON 數據並轉換成 DataFrame。
     4. requests: 取得 YouBike API 的即時數據。
。
  <pre><code>
  import os
  import asyncio
  import pandas as pd
  import requests
  </code></pre>

  - 虛擬導盲器
    
   因為希望製作更不一樣，並且能帶來不同意義的成果，想到導盲犬數量不足夠引導目前的盲人數量，希望製作一個能夠替代導盲犬提示盲者的虛擬導盲犬機器。

   (目前尚在收集資料)
  
- 流程圖
  - 試做版流程圖
    ![image](https://github.com/MocuAcqu/1132Database/blob/main/Youbike%E6%8E%A2%E6%9F%A5%E5%99%A8.png)
  - 虛擬導盲器流程圖
    ![image](https://github.com/MocuAcqu/1132Database/blob/main/%E8%99%9B%E6%93%AC%E5%B0%8E%E7%9B%B2%E5%99%A8.png)
- 預計使用的套件
- 相對應程式碼
