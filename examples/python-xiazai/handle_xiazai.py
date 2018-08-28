#!/usr/bin/env python3.6
# _*_ coding:utf-8 _*_

# 需求：
# 1. 生成一个临时表,表中初步跟xz_article字段一致
# 2. 更新一下临时表中的分类信息
# 3. 
import qrcode
import pyqrcode
import hashlib 
import mysql.connector
import re
import json
import os

config = {
  'user': 'dbuser',
  'password': 'dbuser705',
  'host': '10.10.10.21',
  'port': '5001',
  'database': "3xiazai-handle-fixdown",
  'charset': "utf8",
  'raise_on_warnings': True,
  'use_pure': False,
}

def select():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary =True)
    query = ("select d.id,catid,title,thumb img_md5,keywords,description,url old_url, 1 status," 
    "'未进化的类人猿' writer, '未进化的类人猿' approve_person,FROM_UNIXTIME(UNIX_TIMESTAMP(),'%y-%m-%d %H:%m:%s')"
    ",language,version,filesize,score star,filename,sub_title,self_title,hit_views count,content body,downfiles"
    ",dbycdownload,bddownload,softimage,download_tips from v9_download d left join v9_download_data a on d.id=a.id")
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    cursor.close()
    cnx.close()
    return rows


if __name__ == "__main__":
    # execute only if run as a script
    select()
