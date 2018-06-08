from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from time import sleep
import sqlite3
import re
import sys

sys.path.append("/..")
from util import amazon

def log(file, str):
    file.write(str + "\n")
    print(str)

def confirm_amazon():

    #ページ遷移の待ち時間
    waitSec = 5

    #Amazon画面準備、ログイン
    amazonDriver = webdriver.Chrome("c:/drivers/chromedriver.exe")
    amazonDriver.implicitly_wait(waitSec)
#    amazon.amazon_login(amazonDriver, "hahaha1980@hotmail.co.jp", "cafe1980052")

    #ログファイル準備
    logFile = open("P03Amazon確認.log","w")
    log(logFile, "ログファイルopen")

    #ＤＢを開く
    connection = sqlite3.connect("監視.db")
    cursor = connection.cursor()
    log(logFile, "ＤＢopen")

    try:

        #データ読み込み
        sqlb = []
        sqlb.append(" select yahoo_item_id, amazon_item_url ")
        sqlb.append(" from item_resale ")
        sqlb.append(" where yahoo_cancel_date is null ")
        sqlb.append("  and  yahoo_bid_date is null ")
        sql = "".join(sqlb)
        cursor.execute(sql)

        for row in cursor.fetchall():
            yahoo_item_id = row[0]
            amazon_item_url = row[1]

            amazonDriver.get(amazon_item_url)

            #価格を取得
            amazon_price_now = ""
            amazonElements = amazonDriver.find_elements_by_xpath("//*[contains(@id,'priceblock_')]")
            for amazonElement in amazonElements:
                if not re.match("^priceblock_.*price$" , amazonElement.get_attribute("id")):
                    continue
                amazon_price_now = re.sub(r"[^0-9]", "", amazonElement.text)
                print(amazonElement.get_attribute("id"))
                print(amazon_price_now)
                break

            #在庫数を取得
            amazon_stock_now = ""
            amazonElements = amazonDriver.find_elements_by_id("availability")
            for amazonElement in amazonElements:
                print(amazonElement.text)
                if "在庫あり" in amazonElement.text:
                    amazon_stock_now = 999
                    break
                texts = re.findall("残り[0-9]+点", amazonElement.text)
                if texts:
                    amazon_stock_now = re.sub(r"[^0-9]", "", texts[0])
                    break

            #ＤＢへ書き込み
            item_value = []
            item_value.append(amazon_price_now)
            item_value.append(amazon_stock_now)
            item_value.append(yahoo_item_id)
            sqlb = []
            sqlb.append(" update item_resale set ")
            sqlb.append("  update_date = datetime('now', 'localtime') ")
            sqlb.append(" ,amazon_price_now = ? ")
            sqlb.append(" ,amazon_stock_now = ? ")
            sqlb.append(" where yahoo_item_id = ? ")
            sql = "".join(sqlb)
            cursor.execute(sql,item_value)
            connection.commit()

    finally:
        #ＤＢクローズ
        connection.close()
        #ログファイルクローズ
        logFile.close()
        #Amazon画面クローズ
        amazonDriver.close()
        amazonDriver.quit()

confirm_amazon()