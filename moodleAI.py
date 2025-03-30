from playwright.sync_api import sync_playwright
import os
import csv  # 確保有匯入 csv 模組
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
    page.wait_for_timeout(2000)

    # 使用 .env 讀取帳號密碼
    page.fill("#username", moodle_username)
    page.fill("#password", moodle_pass)

    # 按下登入按鈕
    page.click("button.btn-primary")

    # 等待登入完成
    page.wait_for_timeout(2000)
    print("登入成功！")
    page.screenshot(path="debug_1_after_login.png")

    # 直接前往儀表板
    page.goto("https://moodle3.ntnu.edu.tw/my/")
    page.wait_for_timeout(2000)
    print("進入個人首頁")
    page.screenshot(path="debug_2_after_profile.png")

    # 點擊「moodle 1132個人投資理財 開啟」開啟發文對話框
    post_trigger = page.locator("span:has-text('1132個人投資理財')").first
    post_trigger.wait_for()
    post_trigger.click()
    page.wait_for_timeout(2000)
    print("moodle 1132個人投資理財 開啟")
    page.screenshot(path="debug_3_after_click_post_box.png")

    # 點擊「0226黃金單元課後提問 開啟」開啟發文對話框
    post_trigger = page.locator("span:has-text('0226黃金單元課後提問')").first
    post_trigger.wait_for()
    post_trigger.click()
    page.wait_for_timeout(2000)
    print("0226黃金單元課後提問 開啟")
    page.screenshot(path="debug_4_after_click_post_box.png")

    # 擷取所有學生的發文內容
    posts = page.locator("div.box.py-3.boxaligncenter.full_assignsubmission_onlinetext_2104372 .no-overflow").all_text_contents()

    # 存入 CSV 檔案
    with open("submissions.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["學生發文內容"])  # CSV 標題

        for post in posts:
            writer.writerow([post])

    print("已成功擷取並儲存學生發文內容到 submissions.csv")

    browser.close()

#<div class="box py-3 boxaligncenter full_assignsubmission_onlinetext_2104372" style=""><i class="icon fa fa-minus fa-fw expandsummaryicon contract_assignsubmission_onlinetext_2104372" title="檢視摘要" aria-label="檢視摘要"></i><div class="no-overflow"><p>老師您好，以下是我的提問:</p><p>1.黃金的價值，通常是以與美元的兌換比率來表示，好奇採用美金而非其他國家貨幣幣值的原因，是因為美國是目前黃金儲備量最多的國家嗎?還是有其他因素導致選擇使用美元為標準呢?</p><p>2.初次接觸黃金投資議題的我，看了一些文章後，還是有點不太理解為何川普上任，會導致黃金上漲呢?為什麼關稅政策會大大影響黃金價格呢?</p><p>3.老師上課提過比特幣跟黃金一樣，無法當貨幣，而是可以當投資商品，且黃金跟比特幣都有固定的量，而兩者因為波動性導致能交易的機會不同，我好奇這個波動性是什麼?受什麼影響?</p><p>以上，麻煩老師了，辛苦您與助教了!</p></div></div>