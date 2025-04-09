import os
import time
import json
import pdfkit
import gradio as gr
import pandas as pd
import google.generativeai as genai
from jinja2 import Template
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# ---------- 基本設定 ----------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model_flash = genai.GenerativeModel("gemini-1.5-flash")
model_pro = genai.GenerativeModel("gemini-1.5-pro")

ITEMS = ["修辭使用", "有邏輯", "經驗分享", "前後呼應", "善用譬喻"]

# ---------- HTML 模板 ----------
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

# ---------- 工具函數 ----------
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
# ---------- Github 自動上傳 ----------
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

# ---------- 主分析函數 ----------
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

# ---------- Gradio 介面 ----------
interface = gr.Interface(
    fn=analyze,
    inputs=[
        gr.File(label="上傳作文 CSV", file_types=[".csv"]),
        gr.Textbox(label="額外指令（選填）", placeholder="例如：特別注意邏輯性與例子是否清楚...")
    ],
    outputs=[
        gr.File(label="下載 CSV"),
        gr.File(label="下載 PDF")
    ],
    title="✍️ 作文內容分析與 AI 回饋系統",
    description="請上傳包含學生作文的 CSV（需有 'name', 'content' 欄位），系統會分析是否符合寫作五項標準並產出回饋。"
)

if __name__ == "__main__":
    interface.launch()
