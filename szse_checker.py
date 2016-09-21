# -*- coding: utf-8 -*-

import sys
import random
import requests
import urllib2
import urllib
from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
from datetime import *
import time
import chardet
import os


#指定系统默认编码
reload(sys)
sys.setdefaultencoding('utf8')

RECORDS_FILE = 'records.txt'
BASE_URL = 'http://disclosure.szse.cn/'

def download(url, dirname, filename, records):
    if(url.lower().endswith(".pdf")):
        print "downloading " + url
        
        if not os.path.isdir(dirname):
            print("make dir " + dirname);
            os.mkdir(dirname)
        urllib.urlretrieve(url, os.path.join(dirname,filename + os.path.basename(url)));
        records.append(url)
        path = os.path.join(dirname, RECORDS_FILE)
        writeConfig(path, records)

def readConfig(filename):
    triggerfile = open(filename, "r")
    all = [ line.rstrip() for line in triggerfile.readlines() ]
    lines = []
    for line in all:
        if len(line) == 0 or line[0] == '#':
            continue
        lines.append(line)
    return lines

def writeConfig(path, records):
    # 带加号为可读写
    print 'Update records file...\n'
    hl = open(path, 'w')
    for record in records:
        hl.write(record + "\n")
    hl.close()

def process(url, key_words):
    print 'Fetching data from ' + url

    # 使用webdriver.PhantomJS
    # D:\phantomjs-2.1.1-windows\bin
    browser=webdriver.PhantomJS(executable_path='D:\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe')
    browser.get(url)
    time.sleep(3)
    #设置开始日期
    estart_date = browser.find_element_by_xpath('//input[@id="startTime"]')
    estart_date.clear()
    estart_date.send_keys(str(date.today()))
    #设置结束日期
    eend_date = browser.find_element_by_xpath('//input[@id="endTime"]')
    eend_date.clear()
    eend_date.send_keys(str(date.today() + timedelta(days=1)))
    
    #输入关键字
    for key in key_words:
        keys = key.split(",")
        ekey_code = browser.find_element_by_xpath('//input[@id="stockCode"]')
        ekey_code.clear()
        if len(keys[0]) > 0:
##            print(keys[0].decode("utf-8"))
            ekey_code.send_keys(keys[0].decode("utf-8"))
        ekey_word = browser.find_element_by_xpath('//input[@id="search"]')
        ekey_word.clear()
        if len(keys) > 1 and len(keys[1]) > 0:
##            print(keys[1].decode("utf-8"))
            ekey_word.send_keys(keys[1].decode("utf-8"))
        #提交搜索
        esubmit = browser.find_element_by_xpath('//input[@type="image"][@name="imageField"]')
        esubmit.click()
        time.sleep(3)
        
##        browser.get_screenshot_as_file('show.png')
        
        html = browser.execute_script("return document.documentElement.outerHTML")

        soup = BeautifulSoup(html, "html.parser")
##        write_to_txt(''.join(soup.prettify()))
        hlst = soup.findAll('td', class_='td2')

        print("using keyword " + key.decode("utf-8")  + " get " + str(len(hlst)) + " articles")
        for h in hlst:
            pdate = h.find('span', class_='link1').text.replace("[","").replace("]","").strip()
            path = os.path.join(pdate, RECORDS_FILE)
            if os.path.isfile(path):
                records = readConfig(path)
            else:
                records = []
            region = h.a
            item_url = BASE_URL + region.get('href')
            if item_url in records:
                continue
            item_name = region.text.strip().replace(":","")
            print(item_name.decode("utf-8"))
            download(item_url, pdate, item_name.decode("utf-8"), records)
    print 'done'

def write_to_txt(s):
    # 带加号为可读写
    print 'Write to file...',
    hl = open('./result.txt', 'a')
    hl.write(s)
    hl.close()
    print 'done',

if __name__ == '__main__':
    url_pre = 'http://disclosure.szse.cn/m/drgg.htm'
    triggerlist = readConfig("triggers.txt")
    process(url_pre, triggerlist)

