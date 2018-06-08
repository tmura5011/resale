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

#Amazonにログイン
def amazon_login(amazonDriver, user, pwd):

    #Amazonのトップ画面準備
    amazonDriver.get("https://www.amazon.co.jp/ap/signin?_encoding=UTF8&ignoreAuthState=1&openid.assoc_handle=jpflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.co.jp%2F%3Fref_%3Dnav_signin&switch_account=")

    #hahaha1980@hotmail.co.jp
    #cafe1980052
    amazonDriver.find_element_by_id("ap_email").send_keys(user)
    amazonDriver.find_element_by_id("continue").submit()
    amazonDriver.find_element_by_id("ap_password").send_keys(pwd)
    amazonDriver.find_element_by_id("signInSubmit").submit()


def amazon_buy(amazonDriver, itemUrl):

    #商品画面に移動
    amazonDriver.get(itemUrl)

    #カートに追加
    amazonDriver.find_element_by_id("add-to-cart-button").click()

    #カートの編集
    amazonDriver.find_element_by_id("hlb-view-cart-announce").click()

    #ギフト設定
    amazonDriver.find_element_by_id("sc-buy-box-gift-checkbox").click()
    sleep(5)

    #レジに進む
#    amazonDriver.find_element_by_id("sc-buy-box-ptc-button-announce").click()
    amazonDriver.find_element_by_id("sc-buy-box-ptc-button").click()


    #届け先選択（１つ目）
    amazonDriver.find_elements_by_link_text("この住所を使う")[0].click()

    """
    #届け先入力
    amazonDriver.find_elements_by_id("enterAddressFullName")[0].send_keys("村上　武久")
    amazonDriver.find_elements_by_id("enterAddressPostalCode1")[0].send_keys("602")
    amazonDriver.find_elements_by_id("enterAddressPostalCode2")[0].send_keys("8174")
    Select(amazonDriver.find_elements_by_id("enterAddressStateOrRegion")[0]).select_by_value("京都府")
    amazonDriver.find_elements_by_id("enterAddressAddressLine1")[0].clear()
    amazonDriver.find_elements_by_id("enterAddressAddressLine1")[0].send_keys("京都市上京区分銅町556")
    amazonDriver.find_elements_by_id("enterAddressAddressLine2")[0].send_keys("コンフォート出水207")
    amazonDriver.find_elements_by_id("enterAddressPhoneNumber")[0].send_keys("08031353211")
    #この住所を使う
    amazonDriver.find_elements_by_id("enterAddressAddressLine1")[0].submit()
    """

    #ギフト設定
    amazonDriver.find_element_by_id("includeMessageCheckbox-0").click()
    amazonDriver.find_element_by_id("includeMessageCheckbox-0").submit()

    #発送オプション
    amazonDriver.find_element_by_id("shippingOptionFormId").submit()

    #お支払い方法を選択
    amazonDriver.find_element_by_id("continue-top").click()

    #注文を確定    
#    sleep(5)
#    amazonDriver.find_element_by_name("placeYourOrder1").click()

