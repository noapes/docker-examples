#!/usr/bin/env python3.6
# _*_ coding:utf-8 _*_

## 数据库处理需求
# 1. 将ttrar数据导入到3xiazai保持id自增,注意分类对应
# 2. 处理下载链接
#   a. 如果downfile2 不为空，则 pc_down_url=download.ttrar.com/ + downfile2
#   b. 如果downfile2为空，ycdownload 不为空，则pc_down_url=ycdownload
#   c. 如果downfile2为空，ycsownload 为空，downloadfiles不为空，则pc_down_url=downloadfiles[0]['fileurl']
#   d. 如果downfile2为空，ycsownload 为空，downloadfiles为空,则pc_down_url=title_url + @ + title
# 3. 生成二维码并且更新二维码图片md5值到数据库.

import qrcode
import pyqrcode
import mysql.connector
import re
import json
import os

PATH = "./qrcode"
HOST = "10.10.10.21"
PORT = "5001"
USERNAME = "dbuser"
PASS = "dbuser705"
DBNAME = "3xiazai-handle-B"

config = {
  'user': 'dbuser',
  'password': 'dbuser705',
  'host': '10.10.10.21',
  'port': '5001',
  'database': "3xiazai-handle-B",
  'charset': "utf8",
  'raise_on_warnings': True,
  'use_pure': False,
}


def select():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary =True)
    query = ("SELECT id,downfiles FROM handle_soft where length(downfiles)<>0")
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    cnx.close()
    return rows

def update():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    fileurl2 = handle_download_url()
    for row in fileurl2:
        for (k,v) in row.items():
            query = "update handle_soft set downfiles=%(url)s where id=%(id)s"
            x = cursor.execute(query,{'url':v,'id':k})
            cnx.commit()
            print(x,cursor.statement)
        
            # print(query,x,k,v)
    cursor.close()
    cnx.close()

def handle_softimage():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "select id,softimage from handle_software_data"
    cursor.execute(query)
    rows = cursor.fetchall()
    for id,softimage in rows:
        pattern = '(/.*?\.(?:jpg|gif|png|jpeg))'
        imgs = re.compile(pattern)
        imgs = imgs.findall(softimage)
        query = "update handle_software_data set softimage=%(imgs)s where id=%(id)s"
        x = cursor.execute(query,{'imgs':json.dumps(imgs),'id':id})
        print(x,cursor.statement)
        cnx.commit()
        # print(id,imgs)
    cursor.close()
    cnx.close()

def handle_download_url():
    rows = select();
    fileurl = fileurl1 = fileurl2 = fileurl3 = fileurl4 = []
    for row in rows:
        downfiles = row['downfiles']
        pattern = '((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\"\\\/.,<>?\xab\xbb\u201c\u201d\u2018\u2019]))'
        urls = re.compile(pattern)
        urls = urls.findall(downfiles)
        if len(urls):
            url = urls.pop()
            fileurl2.append({row['id']:url[0]})
        else:
            continue
    return fileurl2
    

if __name__ == "__main__":
    # execute only if run as a script
    handle_softimage() 