import os
import traceback
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

import api_gmail

URL_LOGIN = 'https://accounts.google.com/ServiceLogin?hl=ja&passive=true&continue=https://www.google.com/&ec=GAZAmgQ'

def main():
    driver = webdriver.Chrome(executable_path="chromedriver.exe")
    login(driver, URL_LOGIN)
    sleep(999) # デバッグ用

def login(driver, url):
    driver.get(url)
    try: 
        # Googleログイン画面
        MAIL = driver.find_element(By.ID,'identifierId')
        MAIL.send_keys(os.environ.get('GMAIL_ADDRESS'))
        btn = driver.find_element(By.ID,'identifierNext')
        btn.click()
        sleep(5)
        # SSOログイン画面
        USER = driver.find_element(By.ID,'identifier')
        USER.send_keys(os.environ.get('TUAT_ID'))
        btn = driver.find_element(By.XPATH,'//*[@id="login"]/button')
        btn.click()
        sleep(1)
        object_pass = driver.find_element(By.ID,'password')
        object_pass.send_keys(os.environ.get('TUAT_PASS'))
        btn.click()
        sleep(1)
        # 二段階認証送信
        btn = driver.find_element(By.XPATH,'//*[@id="send-otp-form"]/button')
        btn.click()
        sleep(5)
        # 二段階認証取得
        key = api_gmail.get_auth_key()
        print(key)
        object_key = driver.find_element(By.ID,'emailotp')
        object_key.send_keys(key)
        btn = driver.find_element(By.XPATH,'//*[@id="emailotp-form"]/button')
        btn.click()
        sleep(5)
        # 本人確認
        btn = driver.find_element(By.XPATH,'//*[@id="view_container"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button')
        btn.click()
        return True
    except Exception:
        traceback.print_exc()
        return False

if __name__ == '__main__':
    load_dotenv()
    main()
