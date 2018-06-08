from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from time import sleep
import sqlite3
import re
import sys

#sys.path.append("C:/murakami/クラウド/hayabusa2016/project/resale/src/util")
sys.path.append("/..")
from util import yahoo

def log(file, str):
    file.write(str + "\n")
    print(str)

class YahooCanceledException(Exception):
    pass

def confirm_yahoo():

    #ページ遷移の待ち時間
    waitSec = 5

    #Yahoo画面準備、ログイン
    yahooDriver = webdriver.Chrome("c:/drivers/chromedriver.exe")
    yahooDriver.implicitly_wait(waitSec)
    yahoo.yahoo_login(yahooDriver, "tmura5011@yahoo.co.jp", "94t5092a")

    #ログファイル準備
    logFile = open("../../log/ヤフオク確認.log","w")
    log(logFile, "ログファイルopen")

    #ＤＢを開く
    connection = sqlite3.connect("../../db/resale.db")
    cursor = connection.cursor()
    log(logFile, "ＤＢopen")

    try:

        #データ読み込み
        #キャンセルまたは決済済み以外のもの
        sqlb = []
        sqlb.append(" select ")
        sqlb.append("  yahoo_item_id ")
        sqlb.append(" ,yahoo_item_url ")
        sqlb.append(" ,yahoo_cancel_date ")
        sqlb.append(" ,yahoo_bid_count ")
        sqlb.append(" ,yahoo_bid_last_date ")
        sqlb.append(" ,yahoo_bid_price ")
        sqlb.append(" ,yahoo_bidder_name ")
        sqlb.append(" ,yahoo_bidder_postcode ")
        sqlb.append(" ,yahoo_bidder_address ")
        sqlb.append(" ,yahoo_bidder_contact ")
        sqlb.append(" ,yahoo_pay_date ")
        sqlb.append(" from item_resale ")
        sqlb.append(" where yahoo_cancel_date is null ")
        sqlb.append("  and  yahoo_pay_date is null ")
        sql = "".join(sqlb)
        cursor.execute(sql)

        for row in cursor.fetchall():

            try:
                #前回までのＩＤ、ＵＲＬ、入札数、落札日、入札金額、キャンセル日時、を取得
                yahoo_item_id           = row[0]
                yahoo_item_url          = row[1]
                yahoo_cancel_date       = row[2]
                yahoo_bid_count         = row[3]
                yahoo_bid_last_date     = row[4]
                yahoo_bid_price         = row[5]
                yahoo_bidder_name       = row[6]
                yahoo_bidder_postcode   = row[7]
                yahoo_bidder_address    = row[8]
                yahoo_bidder_contact    = row[9]
                yahoo_pay_date          = row[10]
    
                #ステータス変化を取得
                status_canceled = 0     #キャンセル
                status_last_bidded = 0  #落札済み
                status_paid = 0         #決済済み
    
                #商品のページを開く
                yahooDriver.get(yahoo_item_url)

                try:
                    #落札メッセージを確認
                    bodytext = yahooDriver.find_element_by_xpath("html/body").text
                    if "指定されたドキュメントは存在しません。" in bodytext:
                        raise YahooCanceledException
                    msg = yahooDriver.find_element_by_id("modAlertBox").text

                    #落札メッセージがあるときは、落札
                    if "商品が落札されました" in msg:
                        status_last_bidded = 1

                    #終了のときは、キャンセル扱い
                    elif "オークションは終了しました" in msg:
                        raise YahooCanceledException

                except YahooCanceledException as e:
                    #キャンセル
                    status_canceled = 1

                except:
                    #メッセージが取得できなかったときは、まだ落札されていない
                    #入札数を取得
                    numtext = yahooDriver.find_element_by_class_name("Count__number").text
                    yahoo_bid_count = re.findall("^[0-9]*", numtext)[0]
                    #入札価格を取得
                    numtext = yahooDriver.find_element_by_class_name("Price__value").text
                    yahoo_bid_price = re.findall("^[0-9,]*", numtext)[0].replace(",","")

                #落札されているときは、支払い済みかどうかを確認
                if status_last_bidded:
                    #「取引ナビ」ボタンをクリック
                    btns = yahooDriver.find_elements_by_class_name("libBtnBlueL")
                    for btn in btns:
                        if btn.text == "取引ナビ":
                            btn.click()
                            break
                    #決済済みかどうかをチェック
                    if "支払いを完了しました" in bodytext:
                        status_paid = 1

                #支払い済みのときは、されているときは、取引情報を確認
                if status_paid:
                    #入札数を取得
                    #入札価格を取得
                    pricetext = yahooDriver.find_element_by_class_name("decPrice").text
                    pricetext = re.findall("[0-9, ]*円", pricetext)[0]
                    yahoo_bid_price = re.sub(r"[^0-9]", "", pricetext)
                    elements = yahooDriver.find_elements_by_class_name("libTableCnfTh")
                    #お届け先情報
                    for element in elements:
                        if element.text == "お届け先情報":
                            element = element.find_element_by_xpath("../..")
                            break
                    elements = element.find_elements_by_class_name("decThWrp")
                    for element in elements:
                        #落札者名を取得
                        if element.text == "氏名":
                            element2 = element.find_element_by_xpath("../..")
                            element2 = element2.find_element_by_class_name("decCnfWr")
                            yahoo_bidder_name = element2.text
                            continue
                        #送付先住所を取得
                        if element.text == "住所":
                            element2 = element.find_element_by_xpath("../..")
                            elements2 = element2.find_elements_by_class_name("decCnfWr")
                            yahoo_bidder_postcode = elements2[0].text
                            yahoo_bidder_address = elements2[1].text
                            continue
                        #落札者連絡先を取得
                        if element.text == "電話番号":
                            element2 = element.find_element_by_xpath("../..")
                            element2 = element2.find_element_by_class_name("decCnfWr")
                            yahoo_bidder_contact = element2.text
                            continue
                    
                #ＤＢへ書き込み
                values = []
                values.append(yahoo_item_id)
                sqlb = []
                sqlb.append(" update item_resale set ")
                sqlb.append("  update_date = datetime('now', 'localtime') ")
                #キャンセル日時
                if not yahoo_cancel_date and status_canceled:
                    sqlb.append(" ,yahoo_cancel_date = datetime('now', 'localtime') ")
                #落札日時
                if not yahoo_bid_last_date and status_last_bidded:
                    sqlb.append(" ,yahoo_bid_last_date = datetime('now', 'localtime') ")
                #支払日時
                if not yahoo_bid_price and status_paid:
                    sqlb.append(" ,yahoo_pay_date = datetime('now', 'localtime') ")
                #入札数
                if yahoo_bid_count:
                    sqlb.append(" ,yahoo_bid_count = ? ")
                    values.append(yahoo_bid_count)
                #入札価格
                if yahoo_bid_price:
                    sqlb.append(" ,yahoo_bid_price = ? ")
                    values.append(yahoo_bid_price)
                #落札者名
                if yahoo_bidder_name:
                    sqlb.append(" ,yahoo_bidder_name = ? ")
                    values.append(yahoo_bidder_name)
                #送付先郵便番号
                if yahoo_bidder_postcode:
                    sqlb.append(" ,yahoo_bidder_postcode = ? ")
                    values.append(yahoo_bidder_postcode)
                #送付先住所
                if yahoo_bidder_address:
                    sqlb.append(" ,yahoo_bidder_address = ? ")
                    values.append(yahoo_bidder_address)
                #落札者連絡先
                if yahoo_bidder_contact:
                    sqlb.append(" ,yahoo_bidder_contact = ? ")
                    values.append(yahoo_bidder_contact)
                #where条件
                sqlb.append(" where yahoo_item_id = ? ")
                #ＳＱＬ実行
                sql = "".join(sqlb)
                cursor.execute(sql, values)
                connection.commit()

            except:
                #例外発生時は、エラーを出力して継続
                continue

    finally:
        #ＤＢクローズ
        connection.close()
        #ログファイルクローズ
        logFile.close()
        #Yahoo画面クローズ
        yahooDriver.close()
        yahooDriver.quit()

#単体テスト
if __name__ == "__main__":
    confirm_yahoo()