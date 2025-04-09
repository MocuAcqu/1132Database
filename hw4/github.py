from playwright.sync_api import sync_playwright
import os
import csv  # 確保有匯入 csv 模組
from dotenv import load_dotenv
import asyncio
import pandas as pd
import io
import json
import time
import sys
from google import genai
from google.genai.errors import ServerError

from datetime import datetime
import gradio as gr
import google.generativeai as genai
import pdfkit
from jinja2 import Template

# 根據你的專案結構調整下列 import
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 讀取 .env 檔案
load_dotenv()

#Github
github_username = os.getenv("github_username")
github_pass = os.getenv("github_password")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 顯示瀏覽器
    page = browser.new_page()

    print("啟動瀏覽器，開始登入 moodle...")

    # 進入登入頁面
    page.goto("https://github.com/login")
    page.wait_for_timeout(2000)

    # 使用 .env 讀取帳號密碼
    page.fill("#login_field", github_username)
    page.fill("#password", github_pass)

    # 按下登入按鈕
    post_trigger = page.locator("input:has-text('Sign in')").first
    post_trigger.wait_for()
    post_trigger.click()

    # 等待登入完成
    page.wait_for_timeout(2000)
    print("登入成功！")
    page.screenshot(path="login.png")

    #等待輸入二次驗證
    page.wait_for_timeout(7000)

    content="This is test"
    page.goto("https://github.com/MocuAcqu/1132Database/edit/main/hw4%E5%9B%9E%E9%A5%8B%E5%85%A7%E5%AE%B9")
    page.wait_for_timeout(2000)
    
    # 點擊 CodeMirror 的可編輯區塊以聚焦（選一個內層 div）
    editor = page.locator(".cm-content").first
    editor.click()
    page.keyboard.press("Control+A")  # 如果要清空原有內容
    page.keyboard.press("Backspace")

    # 模擬鍵盤輸入新內容
    content = "This is test"
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

    #<button aria-disabled="false" type="button" data-hotkey="Mod+Enter" class="prc-Button-ButtonBase-c50BI" data-loading="false" data-no-visuals="true" data-size="medium" data-variant="primary" aria-describedby=":r3v:-loading-announcement"><span data-component="buttonContent" data-align="center" class="prc-Button-ButtonContent-HKbr-"><span data-component="text" class="prc-Button-Label-pTQ3x">Commit changes</span></span></button>