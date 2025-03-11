# 資料結構

 - 授課教師：蔡芸琤老師
 - 姓名：邱鈺婷
 - 系級：科技系116

# 作業繳交區


# HW
尋找與確認要研究的方向，完成對程式碼部分的資料抽換及問題抽換，並製作架構圖(流程圖)
- 製作版本
  ## Youbike探查器(試做版) 
  
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

- 讀取環境變數

  <pre><code>
  load_dotenv()
  </code></pre>

-  設定 YouBike API URL

  <pre><code>
  YOUBIKE_API_URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
  </code></pre>

- 取得 YouBike 數據並整理(提取師大附近的車站)
  <pre><code>
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
  </code></pre>

- 非同步處理 YouBike 數據
  <pre><code>
   async def process_chunk(chunk, start_idx, total_records, model_client, termination_condition):
    chunk_data = chunk.to_dict(orient='records')
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
    
    local_data_agent = AssistantAgent("data_agent", model_client)
    local_assistant = AssistantAgent("assistant", model_client)
    local_user_proxy = UserProxyAgent("user_proxy")
    local_team = RoundRobinGroupChat(
        [local_data_agent, local_assistant, local_user_proxy],
        termination_condition=termination_condition
    )
    
    messages = []
    async for event in local_team.run_stream(task=prompt):
        if isinstance(event, TextMessage):
            print(f"[{event.source}] => {event.content}\n")
            messages.append({
                "batch_start": start_idx,
                "batch_end": start_idx + len(chunk) - 1,
                "source": event.source,
                "content": event.content,
                "type": event.type,
                "prompt_tokens": event.models_usage.prompt_tokens if event.models_usage else None,
                "completion_tokens": event.models_usage.completion_tokens if event.models_usage else None
            })
    return messages
  </code></pre>
  - 主程式
    <pre><code>
     async def main():
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("請檢查 .env 檔案中的 GEMINI_API_KEY。")
        return

    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        api_key=gemini_api_key,
    )
    
    termination_condition = TextMentionTermination("exit")
    
    # 取得 YouBike JSON 資料
    df_youbike = fetch_youbike_data()
    if df_youbike is None:
        print("無法處理 YouBike 資料。")
        return
    
    # 設定 chunk_size 分批處理
    chunk_size = 50  # 調整批次大小
    chunks = [df_youbike.iloc[i:i + chunk_size] for i in range(0, df_youbike.shape[0], chunk_size)]
    total_records = df_youbike.shape[0]
    
    tasks = list(map(
        lambda idx_chunk: process_chunk(
            idx_chunk[1],
            idx_chunk[0] * chunk_size,
            total_records,
            model_client,
            termination_condition
        ),
        enumerate(chunks)
    ))
    
    results = await asyncio.gather(*tasks)
    all_messages = [msg for batch in results for msg in batch]
    
    df_log = pd.DataFrame(all_messages)
    output_file = "youbike_analysis_log.csv"
    df_log.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"已將所有對話紀錄輸出為 {output_file}")

 if __name__ == '__main__':
     asyncio.run(main())
     </code></pre>

  ## 虛擬導盲器
    
   因為希望製作更不一樣，並且能帶來不同意義的成果，想到導盲犬數量不足夠引導目前的盲人數量，希望製作一個能夠替代導盲犬提示盲者的虛擬導盲犬機器。

   (目前尚在收集資料)
  
- 流程圖
  - 試做版流程圖
    ![image](https://github.com/MocuAcqu/1132Database/blob/main/Youbike%E6%8E%A2%E6%9F%A5%E5%99%A8.png)
  - 虛擬導盲器流程圖
    ![image](https://github.com/MocuAcqu/1132Database/blob/main/%E8%99%9B%E6%93%AC%E5%B0%8E%E7%9B%B2%E5%99%A8.png)
- 預計使用的套件
- 相對應程式碼
