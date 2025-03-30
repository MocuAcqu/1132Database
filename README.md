# 資料結構

 - 授課教師：蔡芸琤老師
 - 姓名：邱鈺婷
 - 系級：科技系116

# 作業繳交區

# HW1
完成對程式碼部分的資料抽換及問題抽換，並製作架構圖(流程圖)

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



  ## 2. 架構圖
   ![image](https://github.com/MocuAcqu/1132Database/blob/main/youbike.drawio.png)


  ## 3. 使用的AI Agent
  ```
  from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
  from autogen_agentchat.conditions import TextMentionTermination
  from autogen_agentchat.teams import RoundRobinGroupChat
  from autogen_agentchat.messagautogen_agentchat.messageses import TextMessage
  from autogen_ext.models.openai import OpenAIChatCompletionClient
  ```
  ### 3.1 autogen_agentchat.agents
  autogen_agentchat.agents 模組用於初始化該套件提供的各種預定義代理人（agents）。

  AssistantAgent 和 UserProxyAgent這兩個套件屬於自動生成代理人對話系統的一部分。AssistantAgent 負責處理代理人（或機器人）的回應，是一個可整合工具並提供輔助的 AI 代理人，支援同步與非同步回應機制，而 UserProxyAgent 則充當用戶的代理，接收和處理用戶的輸入。
   ```
    local_data_agent = AssistantAgent("data_agent", model_client)
    local_assistant = AssistantAgent("assistant", model_client)
    local_user_proxy = UserProxyAgent("user_proxy")
   ```
****

  ### 3.2 autogen_agentchat.conditions
  autogen_agentchat.conditions 模組提供多代理人團隊（multi-agent teams）行為控制的各種終止條件。
  
  TextMentionTermination這是一個條件模組，用於在對話系統中設定終止對話的條件，通常用於根據文本中的特定提及來終止對話。而這次的程式碼是使用"exit"來當終結對話的特定詞。
  ```
  termination_condition = TextMentionTermination("exit")
  ```
****

  ### 3.3 autogen_agentchat.teams
  autogen_agentchat.teams 模組提供多個預定義的多代理人團隊（multi-agent teams）實作，每個團隊都繼承自 BaseGroupChat (主要用於管理多代理人對話團隊)類別。
  
  RoundRobinGroupChat這個模組實現了循環輪播組聊功能，用於將不同的對話參與者分配給多個team。
  ```
  local_team = RoundRobinGroupChat(
          [local_data_agent, local_assistant, local_user_proxy],
          termination_condition=termination_condition
      )
  ```
****

  ### 3.4 autogen_agentchat.messagautogen_agentchat.messageses
  autogen_agentchat.messages 模組定義了多種用於代理人之間通訊的訊息類型，每種訊息類型都繼承自 BaseChatMessage 或 BaseAgentEvent 類別，主要作用是標準化代理人之間的訊息格式，以確保有效的通訊和互動。
  
  TextMessage這個模組定義了文本訊息的結構，標準化了代理人之間的文字訊息格式，使其能夠在系統內進行一致的處理，用於在系統中處理和生成文本訊息。
   ```
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
   ```

****

  ### 3.5 autogen_ext.models.openai
  autogen_ext.models.openai 模組提供 OpenAIChatCompletionClient 類別，用於與 OpenAI 託管的對話模型進行交互，使他能與OpenAI對話完成模型集成的客戶端，用於向OpenAI模型發送對話提示並接收完成的對話回應。
 ```
     model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        api_key=gemini_api_key,
    )
 ```

# HW2
完成課程中所提到關於DRai的相關程式碼作業，可以自己更改CSV檔案的內容，並提供程式碼執行截圖。

## 【親子對話分析專家】

假設身分為親子對話分析專家，去分析一段錄音逐字對話紀錄中，是否觸及評分項目的標記，並輸出成CSV檔。
| 使用資料  | 程式碼 |
|:--:|:--:|
|[113.csv](https://github.com/MocuAcqu/1132Database/blob/main/DRai/113.csv) | [DRai.py](https://github.com/MocuAcqu/1132Database/blob/main/DRai/DRai.py) |


## 【大學生面試對話分析專家】

假設身分為大學生面試對話分析專家，去分析一段錄音逐字對話紀錄中，是否觸及評分項目的標記，並輸出成CSV檔。(替換老師範例資料)

此對話紀錄來自於AI生成。
| 使用資料 |  程式碼 |
|:--:|:--:|
| [interview.csv](https://github.com/MocuAcqu/1132Database/blob/main/DRai/interview.csv) |[DRai2.py](https://github.com/MocuAcqu/1132Database/blob/main/DRai/DRai2.py) |


# HW3




