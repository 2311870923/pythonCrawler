#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Define a meituan api spider class allows you to fetch meituan
restaurants infos in haikou city.
'''

import csv
import os

import pymysql
import requests
import random

import time

from settings import headers,savePath,filename,sqlConf,tableName,limit
import json



class MT_spider:
    baseUrl = ("http://api.meituan.com/group/v4/deal/select/city/73/cate/20966?"
                "sort=solds&hasGroup=true&mpt_cate1=1&offset={0}&limit={1}")
    modeList = ['txt','csv','mysql']
    tableName = tableName


    #美团深圳地区美食爬虫
    def __init__(self,saveMode = 'txt'):
        if saveMode not in self.modeList:
            raise RuntimeError('存储模式指定有误，请输入txt、csv或者mysql')
        self.saveMode = saveMode

        if self.saveMode == 'mysql':
            self.conn = pymysql.connect(**sqlConf)
            self.cur = self.conn.cursor()

            sql = '''CREATE TABLE IF NOT EXISTS {0}(
                id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
                shopName VARCHAR(60),
                cateName VARCHAR(30),
                avgScore FLOAT,
                areaName VARCHAR(30),
                lat FLOAT,
                lng FLOAT,
                addr VARCHAR(128),
                abstracts TEXT,
                openInfo VARCHAR(128),
                phone VARCHAR(60),
                historyCouponCount INTEGER,
                introduction TEXT,
                featureMenus TEXT
                );'''.format(self.tableName)
            self.cur.execute(sql)
            self.conn.commit()
        else:
            if not os.path.exists(savePath):
                os.makedirs(savePath)
            filePath = os.path.join(savePath,filename+'.'+self.saveMode)
            if not os.access(filePath, os.F_OK):
                with open(filePath, 'w', encoding='utf-8', newline='') as file:
                    if self.saveMode == 'csv':
                        csvwriter = csv.writer(file)
                        csvwriter.writerow(['店铺名称','联系电话', '详细地址'])
            self.file = open(filePath, 'a', encoding='utf-8', newline='')
            if self.saveMode == 'csv':
                self.csvwriter = csv.writer(self.file)
    def run(self, baseurl):
        i = 0
        acquiredCount = 0
        while True:
            url = baseurl.format(str(i*limit), limit)
            print('>>>> url =', url)
            itemlist = self.parse(url)
            if not itemlist:
                break
            for item in itemlist:
                self.save_item(item)
            acquiredCount += len(itemlist)
            print('已成功请求%d个商家信息'%((i+1)*limit))
            print('已成功获取%d个商家信息'%(acquiredCount))
            i += 1
            time.sleep(random.randint(2,5))

    def save_item(self,item):
        if self.saveMode == 'txt':
            for k,v in item.items():
                self.file.write(str(k)+':'+str(v) + '\n')
            self.file.write('\n\n-----------------------------\n\n\n')
        elif self.saveMode == 'csv':
            print('>> writing to csv file.')
            self.csvwriter.writerow(item.values())
        else:
            sql = '''
            INSERT INTO {0}(shopName,cateName,avgScore,areaName,lat,lng,addr,abstracts,openInfo,phone,historyCouponCount,introduction,featureMenus)
            VALUES ('{店铺名称}','{类别}','{评分}','{所属片区}','{纬度}','{经度}','{详细地址}','{优惠套餐情况}','{营业时间}','{联系电话}','{累计售出份数}','{餐厅简介}','{特色菜}')
            '''.format(self.tableName,**item)
            self.cur.execute(sql)
            self.conn.commit()


    def parse(self,url):
        response = requests.get(url,headers=random.choice(headers))
        number = 0
        while True:
            try:
                info_dict = json.loads(response.text)
                info_list = info_dict['data']
                if info_list:
                    break
                else:
                    number += 1
                    if number >= 1:
                        return None
                    time.sleep(10)
                    response = requests.get(url, headers=random.choice(headers))
            except:
                number += 1
                if number >= 1:
                    return None
                time.sleep(10)
                response = requests.get(url, headers=random.choice(headers))

        itemlist = []
        for info in info_list:
            # 店铺名称
            name = info['poi']['name']
            # 所属片区
            areaName = info['poi']['areaName']
            # 详细地址
            addr = info['poi']['addr']
            # 纬度
            lat = info['poi']['lat']
            # 经度
            lng = info['poi']['lng']
            # 餐厅类别
            cateName = info['poi']['cateName']
            # 优惠套餐情况
            abstracts = ''
            for abstract in info['poi']['payAbstracts']:
                # abstracts.append(abstract['abstract'])
                abstracts = abstracts + abstract['abstract'] + ';'

            # 评分
            avgScore = info['poi']['avgScore']
            # 营业时间
            openInfo = info['poi']['openInfo'].replace('\n',' ')
            # 联系电话
            phone = info['poi']['phone']
            # 累计售出份数
            historyCouponCount = info['poi']['historyCouponCount']
            # 餐厅简介
            introduction = info['poi']['introduction']
            # 特色菜
            featureMenus = info['poi']['featureMenus']
            item = {
                '店铺名称': name,
                '联系电话': phone,
                '详细地址': addr
            }

            itemlist.append(item)
        # 返回当前页面item列表
        return itemlist

    def __del__(self):
        if self.saveMode == 'mysql':
            self.cur.close()
            self.conn.close()
        else:
            self.file.close()



# test:
if __name__ == '__main__':
    spider = MT_spider(saveMode='csv')
    urlArr = []

    areaArr = [
        {
            "id": 843, 
            "name": "盱眙", 
            "pinyin": "xuyi", 
            "acronym": "xuyi", 
            "rank": "F", 
            "firstChar": "X"
        }, 
        {
            "id": 862, 
            "name": "丰县", 
            "pinyin": "fengxian", 
            "acronym": "fengxian", 
            "rank": "F", 
            "firstChar": "F"
        }, 
        {
            "id": 875, 
            "name": "睢宁", 
            "pinyin": "suiningxian", 
            "acronym": "suiningxian", 
            "rank": "F", 
            "firstChar": "S"
        }, 
        {
            "id": 948, 
            "name": "江都", 
            "pinyin": "jiangdu", 
            "acronym": "jiangdu", 
            "rank": "E", 
            "firstChar": "J"
        }, 
        {
            "id": 956, 
            "name": "金湖", 
            "pinyin": "jinhu", 
            "acronym": "jinhu", 
            "rank": "F", 
            "firstChar": "J"
        }, 
        {
            "id": 976, 
            "name": "涟水", 
            "pinyin": "lianshui", 
            "acronym": "lianshui", 
            "rank": "F", 
            "firstChar": "L"
        }, 
        {
            "id": 988, 
            "name": "如东", 
            "pinyin": "rudong", 
            "acronym": "rudong", 
            "rank": "E", 
            "firstChar": "R"
        }, 
        {
            "id": 1143, 
            "name": "溧水区", 
            "pinyin": "lishuiqu", 
            "acronym": "lishuiqu", 
            "rank": "F", 
            "firstChar": "L"
        }
    ]
    cateArr = [1, 20, 195, 2, 3, 22, 20375, 20383, 20252, 78, 20007, 20691, 27, 29, 20285, 21365, 20179, 20178, 20274, 20966]
    for i in areaArr:
        for j in cateArr:
            urlArr.append("http://api.meituan.com/group/v4/deal/select/city/"+str(i['id'])+"/cate/"+str(j)+"?sort=solds&hasGroup=true&mpt_cate1=1&offset={0}&limit={1}")

    for url in urlArr:
        spider.run(url)
