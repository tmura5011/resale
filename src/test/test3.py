# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 21:12:46 2018

@author: murakami
"""

from selenium import webdriver

driver = webdriver.Chrome("c:/drivers/chromedriver.exe")
driver.implicitly_wait(5)

driver.get("https://www.amazon.co.jp/o/ASIN/B0179LTNH8/")
itemtext = driver.find_element_by_id("feature-bullets").text

print(itemtext)

# //*[@id="imageBlock"]/div/div/div[2]
# //*[@id="imageBlock"]/div/div/div[2]/div[1]
# //*[@id="main-image-container"]
# //*[@id="main-video-container"]
# //*[@id="video-outer-container"]