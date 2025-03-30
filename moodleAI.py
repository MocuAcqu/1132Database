from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

# 讀取 .env 檔案
load_dotenv()
moodle_username = os.getenv("moodle_username")
moodle_pass = os.getenv("moodle_password")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 顯示瀏覽器
    page = browser.new_page()

    print("啟動瀏覽器，開始登入 moodle...")

    # 進入 Facebook 登入頁面
    page.goto("https://moodle3.ntnu.edu.tw/")
    page.wait_for_timeout(3000)

    # 使用 .env 讀取帳號密碼
    page.fill("#username", moodle_username)
    page.fill("#password", moodle_pass)

    # 按下登入按鈕
    page.click("button.btn-primary")

    # 等待登入完成
    page.wait_for_timeout(3000)
    print("登入成功！")
    page.screenshot(path="debug_1_after_login.png")

    # 直接前往儀表板
    page.goto("https://moodle3.ntnu.edu.tw/my/")
    page.wait_for_timeout(3000)
    print("進入個人首頁")
    page.screenshot(path="debug_2_after_profile.png")
