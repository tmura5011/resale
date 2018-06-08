from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
from time import sleep
import sqlite3
import re

#ログ出力関数
def log(file, str):
    file.write(str + "\n")
    print(str)

#yahooにログイン
def yahoo_login(yahooDriver, user, pwd):

    #yahooのトップ画面準備
    yahooDriver.get("https://login.yahoo.co.jp/config/login")

    #ログイン
    yahooDriver.find_element_by_id("username").send_keys(user)
    yahooDriver.find_element_by_id("btnNext").submit()
    yahooDriver.find_element_by_id("passwd").send_keys(pwd)
    yahooDriver.find_element_by_id("btnSubmit").submit()

def yahoo_cancel(yahooDriver, itemUrl):

    #商品画面に移動
    yahooDriver.get(itemUrl)

    #キャンセル

