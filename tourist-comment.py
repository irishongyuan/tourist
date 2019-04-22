#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 09:57:06 2019

@author: mac
"""
import requests
import requests.packages.urllib3.util.ssl_
import json
import math
import random
import time
import pymysql
from bs4 import BeautifulSoup


def got_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    response = requests.get(url, headers=headers)
    html = response.content.decode()
    return html

def got_htmls(url):
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    response = requests.get(url, headers=headers)
    html = response.content.decode()
    return html

###questionable   
def parse_comment_json_url(html):
    comments = []
    
    json_dict = json.loads(str(html))['data']
    if json_dict==None:
        return comments
    
    remarkList = json_dict['remarkList']
    if remarkList==None:
        return comments
    
    if len(remarkList)>0:
        for item in remarkList:
            remarkTime = item['remarkTime']
            year = int(remarkTime[0:4])
            month = int(remarkTime[5:7])
            if(year<2018 or (year==2018 and month<4)):
                return comments
            
            userName = item['userName']
            userId = item['userId']
            content = item['content']
            comment = {'userName':userName, 'userId':userId, 'comment':content}
            comments.append(comment)
        
        time.sleep(random.random()*3)
        
    return comments
    

def parse_html(html, i):
    global ws  # 全局工作表对象
    
    soup = BeautifulSoup(html, 'lxml')
    item_list = soup.find_all('li', class_ = "list_item")  
    
    db = pymysql.connect(host='114.115.207.35', user='root', password='~F1121abcd', port=3306)
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS spiders DEFAULT CHARACTER SET utf8")
    db = pymysql.connect(host='114.115.207.35', user='root', password='~F1121abcd', port=3306, db='spiders')
    cursor = db.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS tourists (id INT NOT NULL AUTO_INCREMENT, name VARCHAR(255) NOT NULL, area VARCHAR(255) NOT NULL, satisfy VARCHAR(10) NOT NULL, userName VARCHAR(255) NOT NULL, userId INT NOT NULL, comment VARCHAR(255) NOT NULL, PRIMARY KEY (id))'
    cursor.execute(sql)
    table = 'tourists'
    for item in item_list:
        name = item.h3.a.string
        area = item.h3.span.a.string
        satisfy = item.p.strong.string
        #satisfy = item.find('strong', class_="t_ticket").string
        
        pages = int(int(item.p.span.strong.string) / 10)
        
        hrefn='http://menpiao.tuniu.com'+item.h3.a['href']
        content = got_html(hrefn)
        soup1 = BeautifulSoup(content, 'lxml')
        herf = soup1.html.head.link['href']
        stratpos = herf.rfind('/')
        specId = herf[stratpos+1:]
        
        randnum = math.floor(1e32 * random.random())
        
        view = {'name':name, 'area':area, 'satisfy':satisfy}
        
        for pagenum in range(1,pages):
            url = 'https://m.tuniu.com/mapi/tour/getMenpiaoComment?specId='+str(specId)+'&currentPage='+str(pagenum)+'&_='+str(randnum)
            content = got_htmls(url)
            
            if len(parse_comment_json_url(content)) == 0:
                break
            for comment in parse_comment_json_url(content):
                data = view.copy()
                data.update(comment)
                print(data)
                
                keys = ', '.join(data.keys())
                values = ', '.join(['%s'] * len(data))
                sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
                try:
                   if cursor.execute(sql, tuple(data.values())):
                       print('Successful')
                       db.commit()
                except:
                    print('Failed')
                    db.rollback()
    db.close()
                

        

if __name__ == '__main__':
    for i in range(1,268):
        url = 'http://menpiao.tuniu.com/cat_0_0_0_0_0_0_1_1_' + str(i) + '.html'
        print(url)
        content = got_html(url)
        if len(content) < 50:
            break
        
        parse_html(content, i)
