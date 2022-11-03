import datetime
import json
import os
import re
import traceback
from time import sleep

import pandas as pd
import requests
import schedule
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import api_gmail

URL_LOGIN = 'https://accounts.google.com/ServiceLogin?hl=ja&passive=true&continue=https://www.google.com/&ec=GAZAmgQ'
URL_PAGE = 'https://docs.google.com/forms/d/e/1FAIpQLScUUrTcQyKcZXwCWS1Cm66MrdIX7j6kZ43_QppFefVqT60-mQ/viewanalytics'

def main():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=options)
    # Chromeのウィンドウを表示するなら↓を使う
    # driver = webdriver.Chrome(executable_path="chromedriver.exe")
    html = get_html(driver, URL_LOGIN)
    if html is not None:
        df = parse_html(html)
    while(True):
        sleep(30) # 雑なループ
        html = update_html(driver)
        if html is not None:
            _df = parse_html(html)
        if not (_df.compare(df)).empty:
            now = datetime.datetime.now()
            txt = now.strftime('%Y年%m月%d日 %H:%M:%S')+'現在\n```\n'
            for i in range(len(_df)):
                txt += _df['名前'][i]+':'+str(_df['投票数'][i])+'人'
                if _df['投票数'][i]-df['投票数'][i] != 0:
                    txt += '('+str('{:+}'.format(_df['投票数'][i]-df['投票数'][i]))+'人)'
                txt += '\n'
            txt += '```'
            cont = {'content': txt}
            head = {'Content-Type': 'application/json'}
            res = requests.post(os.environ.get('URL_WEBHOOK'), json.dumps(cont), headers=head)
        df = _df

def get_html(driver, url):
    driver.get(url)
    try: 
        # Googleログイン画面
        print('ログイン画面')
        MAIL = driver.find_element(By.ID,'identifierId')
        MAIL.send_keys(os.environ.get('GMAIL_ADDRESS'))
        btn = driver.find_element(By.ID,'identifierNext')
        btn.click()
        sleep(5)
        # SSOログイン画面
        print('SSOログイン画面')
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
        print('二段階認証送信')
        btn = driver.find_element(By.XPATH,'//*[@id="send-otp-form"]/button')
        btn.click()
        sleep(5)
        # 二段階認証取得
        print('二段階認証取得')
        key = api_gmail.get_auth_key()
        print(key)
        object_key = driver.find_element(By.ID,'emailotp')
        object_key.send_keys(key)
        btn = driver.find_element(By.XPATH,'//*[@id="emailotp-form"]/button')
        btn.click()
        sleep(5)
        # 本人確認
        print('本人確認')
        btn = driver.find_element(By.XPATH,'//*[@id="view_container"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button')
        btn.click()
        sleep(1)
        # 投票ページ
        print('投票ページ')
        driver.get(URL_PAGE)
        sleep(5)
        html = driver.page_source
        return html
    except Exception:
        traceback.print_exc()
        return None

def update_html(driver):
    try:
        print('ページ更新')
        driver.refresh()
        sleep(5)
        html = driver.page_source
        return html
    except Exception:
        traceback.print_exc()
        return None

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find('tbody').get_text()
    names = re.split(r'\d+', data)
    names.pop()
    n_votes = list(map(int, re.findall(r'\d+', data)))
    df = pd.DataFrame(list(zip(names, n_votes)), columns=['名前', '投票数'])
    print(df)
    return df

if __name__ == '__main__':
    load_dotenv()
    main()
