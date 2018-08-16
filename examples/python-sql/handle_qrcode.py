#!/usr/bin/env python3.6
# _*_ coding:utf-8 _*_

## 数据库处理需求
# 1. 将ttrar数据导入到3xiazai保持id自增,注意分类对应
# 2. 处理下载链接
#   a. 如果downfile2 不为空，则 pc_down_url=//download.ttrar.com/ + downfile2
#   b. 如果downfile2为空，ycdownload 不为空，则pc_down_url=ycdownload
#   c. 如果downfile2为空，ycsownload 为空，downfiles不为空，则pc_down_url=downfiles[0]['fileurl']
#   d. 如果downfile2为空，ycsownload 为空，downfiles为空,则pc_down_url=title_url + @ + title
# 3. 生成二维码并且更新二维码图片md5值到数据库.
# 4. 区分是pc_down_url,ios_down_url,android_down_url,插入到线上表
# 5. 根据 article表，需要生成一张tiny表，生成层级关系
# 6. 为软件生成m站，20*20的二维码

## 需要生成的表字段
# id,
# cat_id,
# article_id,
# parent_cat_id,
# old_url,cat_url,
# parent_cat_url,
# title,
# createtime,
# seo_title,
# description,
# keywords,
# click,
# abstract,
# status,
# img_md5,
# writer,
# body,approve_date,approve_person,
# is_baidu_push,totaldown,filesize,star,local_img,
# pc_down_url,app_down_url,
# version,soft_update_time,filename,language,
# qrcode,android_down_url,ios_down_url

import qrcode
import pyqrcode
import hashlib 
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
  'user': '',
  'password': '',
  'host': '',
  'port': '',
  'database': "3xiazai-handle-B",
  'charset': "utf8",
  'raise_on_warnings': True,
  'use_pure': False,
}

online = {
  'user': '',
  'password': '',
  'host': '',
  'port': '',
  'database': "sxiazai",
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

# 给每张图片拼接https://www.ttrar.com/ host
def handle_image_with_host():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "select id,softimage from handle_software_data where id<=102158"
    cursor.execute(query)
    rows = cursor.fetchall()
    for id,softimage in rows:
        handle_img = []
        # print(json.loads(softimage))
        for img in json.loads(softimage):
           handle_img.append(img.replace('http','https'))
        query = "update handle_software_data set softimage=%(imgs)s where id=%(id)s"
        x = cursor.execute(query,{'imgs':json.dumps(handle_img),'id':id})
        print(x,cursor.statement)
        cnx.commit()

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
    
def generate_temporary_table():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "select s.id, from handle_software s left join handle_software_data d on s.id=d.id"
    cursor.execute(query)
    rows = cursor.fetchall()
    print(rows,cursor.statement)

def differ_pc_or_app():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    query = "select s.id,downfile2,ycdownload, downfiles,concat('//22859.xc.05cg.com/xiaz/',title,'@',s.filename) lurl,title from handle_software_data d left join handle_software s on d.id=s.id"
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        if row['downfile2'].strip():
            down = "//download.ttrar.com/small/" + row['downfile2']
            if re.search('[0-9a-zA-Z]+\.apk',down):
                x = "update handle_software_data set android_down_url=%(down)s where id= %(id)s"
                cursor.execute(x,{"down":down,"id":row['id']})
                cnx.commit()
                # print(cursor.statement)
            else:
                x = "update handle_software_data set pc_down_url=%(down)s where id= %(id)s"
                cursor.execute(x,{"down":down,"id":row['id']})
                cnx.commit()
                # print(cursor.statement)
        elif row['ycdownload'].strip():
            down = row['ycdownload'].replace('http:','')
            down = down.replace('https:','')
            if re.search('[0-9a-zA-Z]+\.apk',down):
                x = "update handle_software_data set android_down_url=%(down)s where id= %(id)s"
                cursor.execute(x,{"down":down,"id":row['id']})
                cnx.commit()
                # print(cursor.statement)
            else:
                x = "update handle_software_data set pc_down_url=%(down)s where id= %(id)s"
                cursor.execute(x,{"down":down,"id":row['id']})
                cnx.commit()
                # print(cursor.statement)
        elif row['downfiles'].strip():
            down = row['downfiles'].replace('http:','')
            down = down.replace('https:','')
            if re.search('[0-9a-zA-Z]+\.apk',down):
                x = "update handle_software_data set android_down_url=%(down)s where id= %(id)s"
                cursor.execute(x,{"down":down,"id":row['id']})
                cnx.commit()
                print(cursor.statement)
            else:
                x = "update handle_software_data set pc_down_url=%(down)s where id= %(id)s"
                cursor.execute(x,{"down":down,"id":row['id']})
                cnx.commit()
                print(cursor.statement)
        else:
            down = row['lurl']
            x = "update handle_software_data set pc_down_url=%(down)s where id= %(id)s"
            cursor.execute(x,{"down":down,"id":row['id']})
            cnx.commit()
            print(cursor.statement)  
            
def generate_qrcode():
    cnx = mysql.connector.connect(**online)
    cursor = cnx.cursor()
    query = "SELECT id,cat_url,parent_cat_url FROM xz_article WHERE id<=77337 and id>=74031 and parent_cat_url not in ('yxgl','news') and `status` > 0 order by id desc"
    cursor.execute(query)
    rows = cursor.fetchall()
    for id,cat_url,parent_cat_url in rows:
        # print(id,cat_url,parent_cat_url)
        url = "http://m.3xiazai.com/" + parent_cat_url + '/' + cat_url + '/' + str(id) +  '.html'
        # print(url)
        qrcode_xx(url,id)
        

def qrcode_xx(data,id):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    m = hashlib.md5(img.tobytes()).hexdigest()
    dir1 = m[0:2]
    dir2 = m[2:4]
    path = './qrcode/' + dir1 + '/' + dir2 + '/'
    filename = m + '.png'
    if (not os.path.isdir(path)):
        os.makedirs(path)
    print(dir1,dir2,id,data,m)
    print(id,data,m)
    img.save(path + filename)
    update_qrcode(id,m)

def update_qrcode(id,qrcode):
    cnx = mysql.connector.connect(**online)
    cursor = cnx.cursor()
    sql = "update xz_article set qrcode=%(qrcode)s where id=%(id)s"
    cursor.execute(sql,{"qrcode":qrcode,"id":id})
    print(id,cursor.statement)
    cnx.commit()
# def checksum_files():
# def generate_tiny_table():

# def insert_to_online():
if __name__ == "__main__":
    # execute only if run as a script
    generate_qrcode() 