# 資料結構

 - 授課教師：蔡芸琤老師
 - 姓名：邱鈺婷
 - 系級：科技系116

# 作業繳交區

# HW1
尋找與確認要研究的方向，完成對程式碼部分的資料抽換及問題抽換，並製作架構圖(流程圖)

  ## 【Youbike探查器】
  
   - 動機: 嘗試從台北公開資料網站使用Youbike即時資料，特別觀察師大附近幾個特定站點，去判斷建不建議借youbike，以及提醒那些地點無車可借、無位可還。

   - 使用資料: 台北市 YouBike 2.0 API URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"

   - 程式碼參考: 
     - [youbikeAgent.py](https://github.com/MocuAcqu/1132Database/blob/main/youbikeAgent.py)
     - [youbike_analysis_log.csv](https://github.com/MocuAcqu/1132Database/blob/main/youbike_analysis_log.csv)

  ## 1. 資料抽換及問題抽換
我將資料換成台北市 YouBike 2.0 的API，他會每分鐘刷新一次資料，並且特別抓取我需要的幾個站點和站點資訊的欄位來分析。

  ```
# 台北市 YouBike 2.0 API URL
YOUBIKE_API_URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"

def fetch_youbike_data():
    """ 從 API 取得即時 YouBike JSON 並轉換成 DataFrame，僅篩選特定站點 """
    try:
        response = requests.get(YOUBIKE_API_URL)
        response.raise_for_status()
        data = response.json()

        # 轉換 JSON 為 DataFrame
        df = pd.DataFrame(data)

        # 只選擇特定站點
        target_stations = [
            "YouBike2.0_師大公館校區學二舍",
            "YouBike2.0_師範大學公館校區",
            "YouBike2.0_師範大學公館校區_1",
            "YouBike2.0_臺灣師範大學(圖書館)",
            "YouBike2.0_和平龍泉街口",
            "YouBike2.0_臺灣師範大學(浦城街)",
            "YouBike2.0_景美污水抽水站"
        ]
        df = df[df["sna"].isin(target_stations)]

        # 選取需要的欄位
        df = df[["sno", "sna", "total", "available_rent_bikes", "available_return_bikes", "latitude", "longitude"]]
        df.rename(columns={
            "sno": "站點編號",
            "sna": "站點名稱",
            "total": "總車位",
            "available_rent_bikes": "可借車輛數",
            "available_return_bikes": "可還車位數",
            "latitude": "緯度",
            "longitude": "經度"
        }, inplace=True)

        return df
    except Exception as e:
        print(f"無法取得 YouBike 資料: {e}")
        return None
  ```

****

我將我的prompt改成與Youbike站點建議相關的問題，讓我可以根據我想了解的資訊(是否有車可借、有位可還)提出建議，並且定義哪幾站是公館校區和本部校區。

  ```
   prompt = (
        f"目前正在處理第 {start_idx} 至 {start_idx + len(chunk) - 1} 筆 YouBike 站點數據（共 {total_records} 筆）。\n"
        f"以下為該批次 YouBike 即時資訊:\n{chunk_data}\n\n"
        "其中YouBike2.0_師大公館校區學二舍、YouBike2.0_師範大學公館校區、YouBike2.0_師範大學公館校區_1、YouBike2.0_景美污水抽水站位於師大分部；YouBike2.0_臺灣師範大學(圖書館)、YouBike2.0_和平龍泉街口、YouBike2.0_臺灣師範大學(浦城街)位於師大本部\n"
        "請根據以上數據進行分析，並提供完整的 YouBike 站點建議。\n"
        "請特別關注以下方面：\n"
        "  1. 哪些站點即將無車可借？\n"
        "  2. 哪些站點快要沒有車位可還？\n"
        "  3. 是否建議從師大分部，騎腳踏車到師大本部?\n"
        "請各代理人協同合作，提供一份完整且具參考價值的分析。"
    )
  ```



  ## 架構圖
   ![image](https://github.com/MocuAcqu/1132Database/blob/main/Youbike%E6%8E%A2%E6%9F%A5%E5%99%A8.png)


- 預計使用的套件
- 相對應程式碼
  
  TextMentionTermination：設定對話的終止條件。
  RoundRobinGroupChat：管理 AI 代理人的對話方式（輪流回應）。
  OpenAIChatCompletionClient：連接 OpenAI API，使用 gemini-2.0-flash 模型來分析數據。


# 課程練習

## DRai
### 【親子對話分析專家】

假設身分為親子對話分析專家，去分析一段錄音逐字對話紀錄中，是否觸及評分項目的標記，並輸出成CSV檔。
- 使用資料: [113.csv](https://github.com/MocuAcqu/1132Database/blob/main/DRai/113.csv)
- 程式碼: [DRai.py](https://github.com/MocuAcqu/1132Database/blob/main/DRai/DRai.py)


### 【大學生面試對話分析專家】

假設身分為大學生面試對話分析專家，去分析一段錄音逐字對話紀錄中，是否觸及評分項目的標記，並輸出成CSV檔。(替換老師範例資料)

此對話紀錄來自於AI生成。
- 使用資料: [interview.csv](https://github.com/MocuAcqu/1132Database/blob/main/DRai/interview.csv)
- 程式碼: [DRai2.py](https://github.com/MocuAcqu/1132Database/blob/main/DRai/DRai2.py)

