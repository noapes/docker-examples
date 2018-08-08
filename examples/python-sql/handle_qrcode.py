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


def Select():
    cnx = mysql.connector.connect(**config);
    cursor = cnx.cursor()

    query = ("SELECT id,downfiles FROM handle_soft where length(downfiles)<>0 limit 10")

    cursor.execute(query)
    rows = cursor.fetchall()
    handle = []
    for id,handle in rows:
        
  
    cursor.close()
    cnx.close()

if __name__ == "__main__":
    # execute only if run as a script
    Select() 