# 資料結構

 - 授課教師：蔡芸琤老師
 - 姓名：邱鈺婷
 - 系級：科技系116

## 目錄
- ### [HW1](#hw1-1)
  - [資料抽換及問題抽換](#1資料抽換及問題抽換)
  - [架構圖](#2架構圖)
  - [使用的AI Agent](#3使用的ai-agent)
- ### [HW2](#hw2-1)
  - [【DRai 親子對話分析專家】](#drai-親子對話分析專家)
  - [【大學生面試對話分析專家】](#大學生面試對話分析專家)
- ### [HW3](#hw3-1)
- ### [HW4](#hw4-1)

# 作業繳交區

# HW1
完成對程式碼部分的資料抽換及問題抽換，並製作架構圖(流程圖)

  ## 【Youbike探查器】
  
   - 動機: 嘗試從台北公開資料網站使用Youbike即時資料，特別觀察師大附近幾個特定站點，去判斷建不建議借youbike，以及提醒那些地點無車可借、無位可還。

   - 使用資料: 台北市 YouBike 2.0 API URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"

   - 程式碼參考: 
     - [youbikeAgent.py](https://github.com/MocuAcqu/1132Database/blob/main/youbikeAgent.py)
     - [youbike_analysis_log.csv](https://github.com/MocuAcqu/1132Database/blob/main/youbike_analysis_log.csv)

  ## 1.資料抽換及問題抽換
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



  ## 2.架構圖
   ![image](https://github.com/MocuAcqu/1132Database/blob/main/images/youbike.drawio.png)


  ## 3.使用的AI Agent
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

## 【DRai 親子對話分析專家】

假設身分為親子對話分析專家，去分析一段錄音逐字對話紀錄中，是否觸及評分項目的標記，並輸出成CSV檔。
| 使用資料  | 程式碼 |
|:--:|:--:|
|[113.csv](https://github.com/MocuAcqu/1132Database/blob/main/DRai/113.csv) | [DRai.py](https://github.com/MocuAcqu/1132Database/blob/main/DRai/DRai.py) |

****

## 【大學生面試對話分析專家】

假設身分為大學生面試對話分析專家，去分析一段錄音逐字對話紀錄中(此對話紀錄來自於AI生成)，是否觸及評分項目的標記，並輸出成CSV檔。

| 使用資料 |  程式碼 |
|:--:|:--:|
| [interview.csv](https://github.com/MocuAcqu/1132Database/blob/main/DRai/interview.csv) |[DRai2.py](https://github.com/MocuAcqu/1132Database/blob/main/DRai/DRai2.py) |


### 輸出結果截圖
| ![image](https://github.com/MocuAcqu/1132Database/blob/main/images/DRai2_1.png) | ![image](https://github.com/MocuAcqu/1132Database/blob/main/images/DRai2_2.png) |
|--|--|


# HW3
利用Playwright控制瀏覽器，並給予程式碼的執行截圖，截圖方式同HW2

## 【moodle】
| 程式碼 |  輸出結果 |
|:--:|:--:|
| [moodleAI.py](https://github.com/MocuAcqu/1132Database/blob/main/moodleAI.py) |[submissions.csv](https://github.com/MocuAcqu/1132Database/blob/main/submissions.csv) |
   - 動機: 因為想往「批改系統」的方向製作，而想到第一個與我最有關的學生作業作業系統便是Moodle，所以想嘗試讓playwright來控制登入moodle
   - 功能: 此程式可以抓取學生moodle上特定課程的特定作業回答

   - 啟動過程流程圖
     ![image](https://github.com/MocuAcqu/1132Database/blob/main/images/moodleAI.drawio.png)

## 輸出結果截圖
 ![image](https://github.com/MocuAcqu/1132Database/blob/main/images/moodle_1.png) 

| debug_1_after_login |  debug_2_after_profile | debug_3_after_click_post_box |  debug_4_after_click_post_box |
|:--:|:--:|:--:|:--:|
| ![image](https://github.com/MocuAcqu/1132Database/blob/main/images/debug_1_after_login.png) |![image](https://github.com/MocuAcqu/1132Database/blob/main/images/debug_2_after_profile.png) | ![image](https://github.com/MocuAcqu/1132Database/blob/main/images/debug_3_after_click_post_box.png) |![image](https://github.com/MocuAcqu/1132Database/blob/main/images/debug_4_after_click_post_box.png) |

# HW4
利用04/01的範例程式碼，綜合前三項作業內容，生成一個可以下載的PDF

## PDF匯出測試 - 【DRai 親子對話分析】
| 程式碼 | 使用的CSV檔案 | 輸出結果 |
|:--:|:--:|:--:|
| [getPDF.py](https://github.com/MocuAcqu/1132Database/blob/main/DRai/getPDF.py) | [113.csv](https://github.com/MocuAcqu/1132Database/blob/main/DRai/113.csv) | [getPDF.pdf](https://github.com/MocuAcqu/1132Database/blob/main/DRai/getPDF.pdf) |

## 綜合成果 - 【作文內容分析與AI回饋系統】
| 程式碼 | 輸入的CSV檔案 | 輸出的CSV檔案 | 輸出的pdf檔案 | 輸出的github結果 |
|:--:|:--:|:--:|:--:|:--:|
| [github2.py](https://github.com/MocuAcqu/1132Database/blob/main/hw4/github2.py) | [作文資料集.csv](https://github.com/MocuAcqu/1132Database/blob/main/hw4/作文資料集.csv) | [作文回饋.csv](https://github.com/MocuAcqu/1132Database/blob/main/hw4/作文回饋.csv) | [getPDF.pdf](https://github.com/MocuAcqu/1132Database/blob/main/hw4/getPDF.pdf) | [hw4回饋內容](https://github.com/MocuAcqu/1132Database/blob/main/hw4%E5%9B%9E%E9%A5%8B%E5%85%A7%E5%AE%B9)

### 內容說明
本作業是一個作文內容分析與AI回饋系統(延續之前批改系統的想法)，使用者可以在gradio介面輸入CSV檔案(這裡使用"作文資料集.csv")，接著程式會去根據評分項目去分析是否有觸及個項目(有則填"有"，否則"無")，並使用AI Agent去分析文章內容並給予回饋，最後會輸出分析結果的PDF檔案、CSV檔案，且程式會自動登入github，分析結果的文字自動寫入在指定的檔案中，並儲存。

| Gradio介面 | 終端機截圖 |
|:--:|:--:|
|![image](https://github.com/MocuAcqu/1132Database/blob/main/images/hw4_1.png) | ![image](https://github.com/MocuAcqu/1132Database/blob/main/images/hw4_2.png) |

### 程式碼 & 對應作業內容
- **HW1** : 使用AI Agent分析CSV檔案內容、輸出CSV檔案分析結果

  為配合後續欲輸出內容，因此使用Google Gemini API來進行分析CSV檔案的內容。
   ```
   import google.generativeai as genai

   genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
   model_flash = genai.GenerativeModel("gemini-1.5-flash")
   model_pro = genai.GenerativeModel("gemini-1.5-pro")
   ```
   
   ****

- **HW2** : 透過AI Agnet分析每筆CSV檔案資料是否符合評估項目、輸出CSV檔案分析結果

  設定評估項目，並將內容解析成json檔，以及給以分析的prompt。
  ```
  ITEMS = ["修辭使用", "有邏輯", "經驗分享", "前後呼應", "善用譬喻"]

  def parse_response(response_text):
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        result = json.loads(cleaned)
        for item in ITEMS:
            if item not in result:
                result[item] = ""
        return result
    except Exception as e:
        print(f"解析 JSON 失敗：{e}")
        print("原始回傳內容：", response_text)
        return {item: "" for item in ITEMS}

   def score_prompt(content):
       return f"""
   你是一位作文老師，請針對下列作文內容評估是否有觸及以下五項標準：
   1. 修辭使用（如比喻、排比、設問等）
   2. 有邏輯（段落之間有清楚銜接與主題句）
   3. 經驗分享（有分享自身或他人經歷）
   4. 前後呼應（結尾能回扣開頭或主題）
   5. 善用譬喻（是否有明確譬喻幫助說明）
   
   請使用 JSON 格式回應，例如：
   {{
     "修辭使用": "有",
     "有邏輯": "無",
     "經驗分享": "有",
     "前後呼應": "無",
     "善用譬喻": "有"
   }}
   
   作文如下：
   {content}
   """
   
   def feedback_prompt(content):
       return f"""
   你是一位作文老師，請針對以下學生作文給予具體、溫和且有幫助的回饋與建議：
   
   {content}
   
   請使用繁體中文回答。
   """
  ```
  
  ****

- **HW3** : 控自瀏覽器登入網站、進行操作

 自動輸入帳密登入Github(但因為需要雙重認證，目前雙重認證部分仍須手動輸入)，接著跳轉到指定編輯介面(hw4回饋內容)，自動寫入AI Agent分析之內容，並點擊Commit changes進行儲存。
  ```
   def upload_to_github(content: str):
     with sync_playwright() as p:
         browser = p.chromium.launch(headless=False)
         page = browser.new_page()
 
         github_username = os.getenv("github_username")
         github_pass = os.getenv("github_password")
 
         print("登入 GitHub...")
         page.goto("https://github.com/login")
         page.fill("#login_field", github_username)
         page.fill("#password", github_pass)
         page.click("input[name='commit']")
         page.wait_for_timeout(7000)
 
         # 跳轉到目標頁面
         page.goto("https://github.com/MocuAcqu/1132Database/edit/main/hw4%E5%9B%9E%E9%A5%8B%E5%85%A7%E5%AE%B9")
         
         # 點擊 CodeMirror 的可編輯區塊以聚焦（選一個內層 div）
         editor = page.locator(".cm-content").first
         editor.click()
         page.keyboard.press("Control+A")  # 如果要清空原有內容
         page.keyboard.press("Backspace")
 
         page.keyboard.type(content)
 
         # 提交更改
         page.click("button:has-text('Commit changes')")
         page.wait_for_timeout(1000)
 
         # 等待彈窗出現
         page.wait_for_selector("div[role='dialog']")  # GitHub 的 modal 是 dialog 角色
 
         # 點擊彈窗內的第二個 Commit changes
         modal_commit_button = page.locator("div[role='dialog'] button:has-text('Commit changes')").first
         modal_commit_button.wait_for()
         modal_commit_button.click()
         print("點擊彈窗內的 Commit changes")
 
         print("已更新 GitHub 檔案！")
         page.wait_for_timeout(2000)
         browser.close()
  ```

****

- **HW4**練習 : 輸入CSV檔案進行分析並輸出PDF檔案

設定html框架，讓PDF輸出格式固定完整，將分析內容最終可匯出成CSV檔案和PDF檔案。
  ```
   html_template = """
   <!DOCTYPE html>
   <html>
   <head>
     <meta charset="UTF-8">
     <title>作文回饋報告</title>
     <style>
       body { font-family: "Noto Sans TC", sans-serif; margin: 2em; }
       h2 { color: #333; border-bottom: 2px solid #ddd; padding-bottom: 4px; }
       .essay { margin-bottom: 2em; padding: 1em; border: 1px solid #ccc; border-radius: 8px; }
       .feedback { background-color: #f9f9f9; padding: 0.5em; margin-top: 1em; border-left: 4px solid #007bff; }
       .criteria { margin-top: 1em; }
     </style>
   </head>
   <body>
     <h1>作文分析與回饋報告</h1>
     {% for item in results %}
     <div class="essay">
       <h2>{{ item['name'] }}</h2>
       <p><strong>原始內容：</strong> {{ item['content'] }}</p>
       <div class="criteria">
         {% for crit in criteria %}
           <p><strong>{{ crit }}：</strong> {{ item[crit] }}</p>
         {% endfor %}
       </div>
       <div class="feedback">
         <strong>AI 回饋：</strong> {{ item['AI回饋'] }}
       </div>
     </div>
     {% endfor %}
   </body>
   </html>
   """

  def analyze(file, extra_instruction):
    df = pd.read_csv(file)
    results = []

    for _, row in df.iterrows():
        name = row.get("name", "無名")
        content = str(row.get("content", "")).strip()
        if not content:
            continue

        # 評估五項標準
        score_content = score_prompt(content + "\n" + extra_instruction)
        score_response = model_flash.generate_content(score_content)
        score_json = parse_response(score_response.text)

        # AI 回饋
        feedback_content = feedback_prompt(content + "\n" + extra_instruction)
        feedback_response = model_pro.generate_content(feedback_content)
        feedback = feedback_response.text.strip()

        result_row = {
            "name": name,
            "content": content,
            "AI回饋": feedback,
            **score_json
        }
        results.append(result_row)

    # 儲存 CSV，解決中文亂碼
    df_result = pd.DataFrame(results)
    df_result.to_csv("作文回饋.csv", index=False, encoding="utf-8-sig")

    # 儲存 PDF
    html_out = Template(html_template).render(results=results, criteria=ITEMS)
    with open("getHTML.html", "w", encoding="utf-8") as f:
        f.write(html_out)

    pdfkit.from_file("getHTML.html", "getPDF.pdf")

        # 上傳回饋文字至 GitHub
    all_feedback_text = "\n\n".join([f"{r['name']}：\n{r['AI回饋']}" for r in results])
    upload_to_github(all_feedback_text)

    return "作文回饋.csv", "getPDF.pdf"
  ```



