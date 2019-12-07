import requests,csv,random
import json
import jsonpath
import time
from lxml import etree
import redis
from bs4 import BeautifulSoup

from settings import url, detail_url,uuid, originUrl
from tool.create_token.meituan.createtoken import CreatTokenForMeituan


class Meituan(object):
    def __init__(self, *args, **kwargs):
        self.redis = redis.Redis(host='47.105.174.154', port=6379,db=0)
        self.url = url
        self.detail_url = detail_url
        self.cityName = kwargs.get("cityName","博白县")
        self.cateId = kwargs.get("cateId",0)
        self.areaId = kwargs.get("areaId",0)
        self.sort = kwargs.get("sort","")
        self.dinnerCountAttrId = kwargs.get("dinnerCountAttrId","")
        self.page = kwargs.get("page",1)
        self.userId = kwargs.get("userId","")
        self.uuid = uuid
        self.platform = kwargs.get("platform",1)
        self.partner = kwargs.get("partner",126)
        self.originUrl = originUrl
        self._token = None
        self.payload = {
            "cityName": self.cityName,
            "cateId": self.cateId,
            "areaId": self.areaId,
            "sort": self.sort,
            "dinnerCountAttrId": self.dinnerCountAttrId,
            "page": self.page,
            "userId": self.userId,
            "uuid": self.uuid,
            "platform": self.platform,
            "partner": self.partner,
            "originUrl": self.originUrl,
            "_token": self._token,
        }
        self.headers = {
            "Host": "bj.meituan.com",
            "Referer": "http://bj.meituan.com/meishi/pn3/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        }

    def get_response(self):
        #p = requests.get(url='http://47.105.174.154:9999/pop')
        response = requests.get(url=self.url, params=self.payload, timeout=6.0, headers=self.headers)
        try:
            return json.loads(response.content.decode())
        except:
            self.payload["_token"] = CreatTokenForMeituan.creatToken()
            # print(self._token)
            try:
                response = requests.get(url=self.url, params=self.payload, timeout=6.0, headers=self.headers)
                return json.loads(response.content.decode())
            except Exception as e:
                input("请先手动登录, 完成后按回车继续:")
                self.payload["_token"] = CreatTokenForMeituan.creatToken()
                response = requests.get(url=self.url, params=self.payload, timeout=6.0, headers=self.headers)
                return json.loads(response.content.decode())

    def processing_data(self, data):
        try:
            data = jsonpath.jsonpath(data, '$..poiInfos')[0]
        except Exception as e:
            return False 
        return data
    def run(self):
        data = self.get_response()
        data = self.processing_data(data)
        if(data):
            self.detail(data)
        #time.sleep(10*60)
        return data
    def detail(self, data):
        for i in data:
            #tnum = random.randint(1,3)
            #print ('防止网站禁止爬虫，等待%s秒' % tnum)
            #time.sleep(tnum)
            detailUrl = self.detail_url.format(poid=i['poiId'])
            self.headers['Upgrade-Insecure-Requests'] = '1'
            try:
                #p = requests.get(url='http://47.105.174.154:9999/pop')
                print(detailUrl)
                response = requests.get(url=detailUrl, timeout=6.0, headers=self.headers)
                soup = BeautifulSoup(response.text, "html.parser")
                code = soup.find('img', {'id': 'yodaImgCode'})
                if code:
                    input("请先手动登录, 完成后按回车继续:")
                    response = requests.get(url=detailUrl, timeout=6.0, headers=self.headers)

            except Exception as e:
                return
            response.encoding = 'utf-8'
            html = etree.HTML(response.text)
            datas = html.xpath('body/script')
            for data in datas:
                try:
                    strs = data.text[:16]
                    if strs == 'window._appState':
                        result = data.text[19:-1]
                        result = json.loads(result)
                        name = result['detailInfo']['name']
                        addr = result['detailInfo']['address']
                        phone = result['detailInfo']['phone']
                        aveprice = result['detailInfo']['avgPrice']
                        opentime = result['detailInfo']['openTime']
                        avescore = result['detailInfo']['avgScore']
                        had = self.redis.get(phone)
                        if had is None:
                            self.redis.set(phone, name) 
                            print ('商家名称: %s' % name)
                            print ('商家电话: %s' % phone)
                            print ('商家地址: %s' % addr)
                            print ('平均消费: %s' % aveprice)
                            print ('开业时间: %s' % opentime)
                            print ('评分: %s' % avescore)
                            print ('\n')
                            conpany_msg = (name,phone,addr,aveprice,opentime,avescore)
                            with open('meituan_company.csv','a',newline='',encoding='utf-8-sig') as datacsv:
                                csvwriter = csv.writer(datacsv,dialect=('excel'))
                                csvwriter.writerow(conpany_msg)

                except:
                    pass
if __name__ == '__main__':
    meituan = Meituan()
    meituan.run()