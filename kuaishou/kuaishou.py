import hashlib, time
import requests
import os,requests,sys,csv,random,threading,re
from bs4 import BeautifulSoup
import pyquery
from datetime import datetime
import math
import redis

csv_List_head=('快手ID','昵称','性别','简介', '城市')

#保存数据到csv文件
def save_csv(msg):
    with open('kuaishou.csv','a',newline='',encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(msg)

#保存数据到csv文件
def save_csv_city(msg, prov):
    if not prov:
        prov = '未知区域'
    if not os.path.exists('kuaishou'+prov+'.csv'):#文件不存在，创建文件
        with open('kuaishou'+prov+'.csv', 'a+', newline='', encoding='utf-8-sig') as datacsv:
            csvwriter = csv.writer(datacsv, dialect=('excel'))
            csvwriter.writerow(csv_List_head)
    with open('kuaishou'+prov+'.csv','a',newline='',encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(msg)

def getToken(userId):
    userId = '%d'%userId
    str = 'app=0appver=6.3.0.8671c=XIAOMIclient_key=3c2cd3f3country_code=cndid=ANDROID_1bfcbbf139010fb3did_gt=1554807821702ftt=hotfix_ver=isp=CMCCiuid=kpf=ANDROID_PHONEkpn=KUAISHOUlanguage=zh-cnlat=0lon=0max_memory=512mod=Xiaomi(MI 8)net=WIFIoc=XIAOMIos=androidsys=ANDROID_9token=e28390b9b5d945b5955e81023f8760ac-749381306ud=749381306user='+userId+'ver=6.3382700b563f4'
    str = bytes(str, encoding='utf8')
    m = hashlib.md5()
    m.update(str)
    sign = m.hexdigest()
    return sign

def getCommentToken(userId, photoId):
    userId = '%d'%userId
    photoId = '%d' % photoId
    str = 'app=0appver=6.3.0.8671c=XIAOMIclient_key=3c2cd3f3count=1000country_code=cndid=ANDROID_1bfcbbf139010fb3did_gt=1554807821702ftt=hotfix_ver=isp=CMCCiuid=kpf=ANDROID_PHONEkpn=KUAISHOUlanguage=zh-cnlat=0lon=0max_memory=512mod=Xiaomi(MI 8)net=WIFIoc=XIAOMIorder=descos=androidphotoId='+photoId+'photoPageType=3sys=ANDROID_9token=86d272b575b7433d98d2c9a65426b449-749381306ud=749381306user_id='+userId+'ver=6.3382700b563f4'
    str = bytes(str, encoding='utf8')
    m = hashlib.md5()
    m.update(str)
    sign = m.hexdigest()
    return sign



def getDetail(userId):
    sign = getToken(userId)

    url = 'http://api.gifshow.com/rest/n/user/profile/v2'

    dataStr = "app=0&kpf=ANDROID_PHONE&ver=6.3&c=XIAOMI&mod=Xiaomi(MI 8)&appver=6.3.0.8671&ftt=&isp=CMCC&kpn=KUAISHOU&lon=0&language=zh-cn&sys=ANDROID_9&max_memory=512&ud=749381306&country_code=cn&oc=XIAOMI&hotfix_ver=&did_gt=1554807821702&iuid=&net=WIFI&did=ANDROID_1bfcbbf139010fb3&lat=0&user="+str(userId)+"&token=e28390b9b5d945b5955e81023f8760ac-749381306&sig="+sign+"&client_key=3c2cd3f3&os=android&__NStokensig=e240462bd2cff641e71c802df8be961d107b435f44670ff362564331d013ce8e"

    data = {i.split('=')[0]: i.split('=')[1] for i in dataStr.split('&')}

    headers = {
        'Host': 'api.gifshow.com'
    }

    req = requests.post(url, data=data, headers=headers)



    name  = req.json()['userProfile']['profile']['user_name']
    brief = req.json()['userProfile']['profile']['user_text']
    id    = req.json()['userProfile']['profile']['user_id']
    print(brief)
    try:
        city = req.json()['userProfile']['cityName']
        prov  = req.json()['userProfile']['cityName'].split(' ')[0]
    except Exception:
        city = ''
        prov = ''

    try:
        kid = req.json()['userProfile']['profile']['kwaiId']
    except Exception:
        kid = ''
    sex   = req.json()['userProfile']['profile']['user_sex']

    if sex == 'M':
        sex = '男'
    else:
        sex = '女'

    r = redis.Redis(host='47.105.174.154', port=6379, db=0)
    had = r.get('kuaishouid-'+str(id))
    user_msg = (kid, name, sex, brief, city)
    pattern = re.compile('[A-Z]+|[a-z]+|[0-9]]+')
    match = pattern.findall(brief)
    if (had is None) and brief and len(match)>0:
        r.set('kuaishouid-'+str(id), id)
        print('用户ID: %s' % id)
        print('快手ID: %s' % kid)
        print('用户名: %s' % name)
        print('性别: %s' % sex)
        print('简介: %s' % brief)
        print('城市: %s' % city)
        save_csv(user_msg)
        save_csv_city(user_msg, prov)
    #exit()
    #print(req.json()['userProfile']['profile']['user_text'])

def getDetailUserInfo(userId, photoId):
    sign = getCommentToken(userId, photoId)

    url = 'http://api.gifshow.com/rest/n/comment/list/v2'

    dataStr = "app=0&kpf=ANDROID_PHONE&ver=6.3&c=XIAOMI&mod=Xiaomi(MI 8)&appver=6.3.0.8671&ftt=&isp=CMCC&kpn=KUAISHOU&lon=0&language=zh-cn&sys=ANDROID_9&max_memory=512&ud=749381306&country_code=cn&oc=XIAOMI&hotfix_ver=&did_gt=1554807821702&iuid=&net=WIFI&did=ANDROID_1bfcbbf139010fb3&lat=0&photoId="+str(photoId)+"&user_id="+str(userId)+"&order=desc&count=1000&photoPageType=3&token=86d272b575b7433d98d2c9a65426b449-749381306&sig=" + sign + "&client_key=3c2cd3f3&os=android&__NStokensig=e240462bd2cff641e71c802df8be961d107b435f44670ff362564331d013ce8e"
    data = {i.split('=')[0]: i.split('=')[1] for i in dataStr.split('&')}

    headers = {
        'Host': 'api.gifshow.com'
    }

    req = requests.post(url, data=data, headers=headers)

    userList = []
    infoList = req.json()['rootComments']
    for info in infoList:
        userList.append(info['author_id'])

    for userId in userList:
        r = redis.Redis(host='47.105.174.154', port=6379, db=0)
        had = r.get('kuaishouid-' + str(userId))
        if (had is None):
            print(userId)
            getDetail(userId)
            time.sleep(6)


def getList():
    url = 'http://api.gifshow.com/rest/n/feed/hot'

    dataStr = "app=0&kpf=ANDROID_PHONE&ver=6.3&c=XIAOMI&mod=Xiaomi(MI 8)&appver=6.3.0.8671&ftt=&isp=CMCC&kpn=KUAISHOU&lon=0&language=zh-cn&sys=ANDROID_9&max_memory=512&ud=749381306&country_code=cn&pm_tag=&oc=XIAOMI&hotfix_ver=&did_gt=1554807821702&iuid=&extId=66e308393f71e8093cf8a7af07814b60&net=WIFI&did=ANDROID_1bfcbbf139010fb3&lat=0&type=7&page=1&coldStart=false&count=20&pv=false&id=17&refreshTimes=2&pcursor=&source=1&needInterestTag=false&browseType=1&seid=da94e550-fd5e-4413-b95e-58801ee0a81f&os=android&__NStokensig=f45e92f94c4cff3007552e6a899576e244780a0c9d08298a19f554cec9b5947c&token=e28390b9b5d945b5955e81023f8760ac-749381306&sig=d0e362e6c350ca3c147af3124bc63d28&client_key=3c2cd3f3"

    data = {i.split('=')[0]: i.split('=')[1] for i in dataStr.split('&')}

    headers = {
        'Host': 'api.gifshow.com'
    }

    req = requests.post(url, data=data, headers=headers)
    userList = []
    infoList = req.json()['feeds']
    for info in infoList:
        r = redis.Redis(host='47.105.174.154', port=6379, db=0)
        had = r.get('kuaishouid-' + str(info['user_id']))
        if (had is None):
            userList.append(info['user_id'])
        # 抓取详情用户的信息
        #getDetailUserInfo(info['user_id'], info['photo_id'])

    return userList

def main():
    while True:
        userList = getList()
        for userId in userList:
            getDetail(userId)
            #time.sleep(1)
        #exit()
        #time.sleep(10)

if __name__ == '__main__':
    # 获取爬虫开始时间
    start_time = datetime.now()
    print ('获取快手用户信息')
    print ('爬虫开始')
    # csv文件表格的列表头
    '''with open('kuaishou.csv','a+',newline='',encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(csv_List_head)'''
    main()
    #获取爬虫结束时间
    end_time = datetime.now()
    #获取爬虫花费的时间
    use_time = end_time - start_time
    print ('爬虫结束,耗时%s，数据保存在qichacha_company.csv中' % use_time)
