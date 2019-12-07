#!/usr/bin/env python3

import os, requests, sys, csv, time, random, threading
from bs4 import BeautifulSoup
from datetime import datetime
import json
import redis
import math
import re
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ChromeOptions
from io import BytesIO
from PIL import Image, ImageEnhance
from PIL import Image
from PIL import ImageGrab
import cv2

# 大众点评页面起止
list_url = 'http://www.dianping.com/search/map/ajax/json'
detail_url = 'https://www.dianping.com/shop/{shopId}'
# 请求头
headers = {
    'Host': 'www.dianping.com',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
}

_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
}

cookies_str = '_lxsdk_cuid=1688917eef6c8-06a15647cde66a-10376655-1fa400-1688917eef7c8; _lxsdk=1688917eef6c8-06a15647cde66a-10376655-1fa400-1688917eef7c8; _hc.v="9d734ecb-8555-47f6-8acc-ca8c2045ba5b.1548488274"; s_ViewType=10; aburl=1; cy=2; cye=beijing; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1554723400; wedchatguest=g186338361423507522; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _dp.ac.v=10fac4a2-5ee4-438c-9b30-f00de3e64c4c; lgtoken=0b3de4b33-b11a-411f-b44f-5c7f47c9729f; dper=3a5731b742657415f5ec517cee0d2fb49b800de9def0c30bb51b6dc740802c2ae75a87ab41327859ab8685b6edcfc69a936f49f714250439b928d0b731ee6aa0438752ac75caa3a1be8b531e2534a52dce68c6d1c1f8b292fe96a43a825ab56c; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_8571880941; ctu=50ed51cf16794a23e2466c4af4c57865ce740eca1190a2af950e3b53383d3aa7; uamo=15737135239; _lxsdk_s=16a168cf083-20c-2bc-c4d%7C%7C16'

cookies = {i.split('=')[0]: i.split('=')[1] for i in cookies_str.split('; ')}

#proxies = None

font_size = 14
start_y = 23

PROXY = "http://127.0.0.1:8080"

# csv的列表头
csv_List_head = ('店铺名称', '联系电话', '地址')

with open("test.txt", "r")as f:
    one = f.read()

def getProxies():
    '''proxies = requests.get("http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&pack=34788&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=")
    return {
        'http': "http://"+proxies.text.strip(),
        'https': "http://"+proxies.text.strip()
    }'''
    return None

# 保存数据到csv文件
def save_csv(msg):
    with open('dazhongdianping.csv', 'a', newline='', encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv, dialect=('excel'))
        csvwriter.writerow(msg)


def getCityList():
    with open("./JSON/active_cities.json", "r") as f:
        citys_dict = json.load(f)
        #citys_dict = citys_dict[47:]
        #print(citys_dict)
        #print(len(citys_dict))
        #exit()
        return citys_dict


def getShopList(i):
    data = {
        'cityId': i['cityId']
    }
    response = requests.post(list_url, headers=headers, data=data, cookies=cookies, timeout=6.0, proxies=getProxies())
    try:
        pageDict = json.loads(response.text)
    except Exception as e:
        listpojie()
        #input("请先手动登录列表, 完成后按回车继续1:")
        response = requests.post(list_url, headers=headers, data=data, cookies=cookies, proxies=getProxies())
        pageDict = response.json()

    pageCount = pageDict['pageCount']
    if pageCount > 50:
        pageCount = 50

    start_page = open('page.txt', 'r').read() if os.path.isfile('page.txt') else '5'
    for pageNum in range(int(start_page), pageCount + 1):
        open('page.txt', 'wb').write(str(pageNum).encode('utf-8'))
        print(i['cityName']+"第"+str(pageNum)+"页数据")
        data['page'] = pageNum
        response = requests.post(list_url, headers=headers, data=data, cookies=cookies,proxies=getProxies())
        try:
            repDict = json.loads(response.text)
        except Exception:
            listpojie()
            #input("请先手动登录列表, 完成后按回车继续:")
            response = requests.post(list_url, headers=headers, data=data, cookies=cookies,proxies=getProxies())
            repDict = response.json()
        shopList = repDict['shopRecordBeanList']
        getShopDetail(shopList)

def listpojie():
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    desired_capabilities = options.to_capabilities()
    desired_capabilities['acceptSslCerts'] = True
    desired_capabilities['acceptInsecureCerts'] = True
    desired_capabilities['proxy'] = {
        "httpProxy": PROXY,
        "ftpProxy": PROXY,
        "sslProxy": PROXY,
        "noProxy": None,
        "proxyType": "MANUAL",
        "class": "org.openqa.selenium.Proxy",
        "autodetect": False,
    }

    cookies_str = '_lxsdk_cuid=1688917eef6c8-06a15647cde66a-10376655-1fa400-1688917eef7c8; _lxsdk=1688917eef6c8-06a15647cde66a-10376655-1fa400-1688917eef7c8; _hc.v=9d734ecb-8555-47f6-8acc-ca8c2045ba5b.1548488274; s_ViewType=10; aburl=1; _dp.ac.v=10fac4a2-5ee4-438c-9b30-f00de3e64c4c; dper=3a5731b742657415f5ec517cee0d2fb49b800de9def0c30bb51b6dc740802c2ae75a87ab41327859ab8685b6edcfc69a936f49f714250439b928d0b731ee6aa0438752ac75caa3a1be8b531e2534a52dce68c6d1c1f8b292fe96a43a825ab56c; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_8571880941; ctu=50ed51cf16794a23e2466c4af4c57865ce740eca1190a2af950e3b53383d3aa7; uamo=15737135239; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1554723400,1555208290; cy=2; cye=beijing; Hm_lpvt_dbeeb675516927da776beeb1d9802bd4=1555208340; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_s=16a2a4880da-32d-623-c55%7C%7C60'
    cookies = {i.split('=')[0]: i.split('=')[1] for i in cookies_str.split('; ')}

    driver = webdriver.Chrome(executable_path="/Users/echo/Documents/sites/wxhub-master/chromedriver", options=options, desired_capabilities=desired_capabilities)
    driver.get(list_url)
    for key, item in cookies.items():
        driver.add_cookie({
            'domain': 'www.dianping.com',
            'name': key,
            'value': item,
            'path': '/',
            'expires': ""
        })
    driver.get(list_url)
    #input("请先手动登录列表, 完成后按回车继续")
    time.sleep(2)
    while True:
        try:
            driver.find_element_by_xpath('//*[@id="yodaImgCodeInput"]')
            time.sleep(50)
            continue
        except:
            try:
                driver.find_element_by_xpath('//*[@id="root"]/div')
                time.sleep(50)
                continue
            except Exception:
                time.sleep(3)
                driver.quit()
                return

    '''driver.save_screenshot('code.png')

    img = cv2.imread("code.png")
    cropped = img[197:238, 560:642]
    cv2.imwrite("code_crop.png", cropped)
    code = input("请先手动列表, 完成后按回车继续:")
    elem_user = driver.find_element_by_xpath('//*[@id="yodaImgCodeInput"]')
    elem_user.send_keys(code)
    elem_btn = driver.find_element_by_xpath('//*[@id="yodaImgCodeSure"]')
    time.sleep(3)
    elem_btn.click()'''

def detailpojie(detailUrl):
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    desired_capabilities = options.to_capabilities()
    desired_capabilities['acceptSslCerts'] = True
    desired_capabilities['acceptInsecureCerts'] = True
    desired_capabilities['proxy'] = {
        "httpProxy": PROXY,
        "ftpProxy": PROXY,
        "sslProxy": PROXY,
        "noProxy": None,
        "proxyType": "MANUAL",
        "class": "org.openqa.selenium.Proxy",
        "autodetect": False,
    }
    driver = webdriver.Chrome(executable_path="/Users/echo/Documents/sites/wxhub-master/chromedriver", options=options, desired_capabilities=desired_capabilities)
    driver.get(detailUrl)
    while True:
        try:
            driver.find_element_by_xpath('//*[@id="body"]')

            try:
                driver.find_element_by_xpath('//*[@id="root"]/div')
                time.sleep(30)
                continue
            except Exception:
                time.sleep(3)
                driver.quit()
                return
        except:
            time.sleep(30)
            continue

    '''time.sleep(10)
    slider = driver.find_element_by_xpath('//*[@id="yodaBox"]')
    ActionChains(driver).click_and_hold(slider).perform()
    tracks = [5, 6, 3, 8, 5, 3, 1, 11, 20, 10, 5,5,5, 6, 3, 8, 5, 3, 1, 11, 100, 10, 5,5, 6, 3, 8, 5, 3, 5, 6, 3, 8, 5, 3, 1, 11, 20, 10, 5,5,5, 6, 3, 8, 5, 3, 1, 11, 20, 10, 5,5, 6, 3, 8, 5, 3, 1, 11, 20, 10, 5,5, 6, 3, 8, 5, 3, 1, 11, 20, 10, 5,5, 6, 3, 8, 5, 3, 1, 11, 20, 10, 5]
    for track in tracks:
        time.sleep(0.02)
        ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()

    while True:
        error = driver.find_element_by_xpath('//*[@id="root"]/div')
        print(error)
        if(error):
            driver.refresh()
            time.sleep(3)
            try:
                slider = driver.find_element_by_xpath('//*[@id="yodaBox"]')
            except Exception:
                return
            ActionChains(driver).click_and_hold(slider).perform()
            tracks = [5, 6, 3, 8, 5, 3, 1, 11, 20, 10, 5, 5, 5, 6, 3, 8, 5, 3, 1, 11, 100, 10, 5, 5, 6, 3, 8, 5, 3, 5,
                      6, 3, 8, 5, 3, 1, 11, 20, 10, 5, 5, 5, 6, 3, 8, 5, 3, 1, 11, 20, 10, 5, 5, 6, 3, 8, 5, 3, 1, 11,
                      20, 10, 5, 5, 6, 3, 8, 5, 3, 1, 11, 20, 10, 5, 5, 6, 3, 8, 5, 3, 1, 11, 20, 10, 5]
            for track in tracks:
                time.sleep(0.01)
                ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()

        else:
            return'''



def getShopDetail(shopList):
    for i in shopList:
        #time.sleep(3)
        detailUrl = detail_url.format(shopId=i['shopId'])
        #detailUrl = detail_url.format(shopId='69828435')
        print(detailUrl)
        try:
            response = requests.get(detailUrl, headers=headers, cookies=cookies, allow_redirects=False, timeout=6.0,proxies=getProxies())
        except Exception:
            continue

        if response.status_code == 302:
            time.sleep(1)
            response = requests.get(detailUrl, headers=headers, cookies=cookies, allow_redirects=False, timeout=6.0,proxies=getProxies())

        soup = BeautifulSoup(response.text, "html.parser")
        print(response.status_code)
        if response.status_code == 200 or response.status_code == 302:
            if response.status_code == 302:
                if 'verify.meituan.com' in response.headers['Location']:
                    detailpojie(detailUrl)
                    #input("请先手动登录详情, 完成后按回车继续:")
                    try:
                        response = requests.get(detailUrl, headers=headers, cookies=cookies, timeout=6.0,proxies=getProxies())
                    except Exception:
                        continue
                    soup = BeautifulSoup(response.text, "html.parser")
                else:
                    continue
            try:
                shopname = soup.find('h1', {'class': 'shop-name'}).text.strip()
                shopname = soup.find('h1', {'class': 'shop-name'})
                shopname = re.sub('<a.*?>.*?</a>', '', str(shopname))
                shopname = re.sub(r'<.*?>', '', shopname).strip()

            except Exception:
                try:
                    shopname = soup.find('h1').text.strip()
                except Exception:
                    continue

            shopname = re.sub('手机买单 积分抵现', '', shopname)
            #address = get_address(response.text)
            address=''
            '''if address is False:
                try:
                    address = soup.find('span', {'class': 'info-name'}).text.strip()
                except Exception:
                    try:
                        address = soup.find('a', {'class': 'region'}).text.strip()
                    except Exception:
                        try:
                            address = soup.find('div', {'class': 'address'}).text.strip()
                        except Exception:
                            address = ""

                if address == "地址：":
                    soup.find('div', {'class': 'address'}).find('span', {'class': 'item'}).text.strip()'''
            phone = get_phone(response.text)
            if (phone is False) or phone == '0-':
                try:
                    phone = soup.find('p', {'class': 'tel'}).find('span', {'class': 'item'}).text.strip()
                except Exception:
                    try:
                        phone = soup.find('i', {'class': 'icon-tel'}).text.strip()
                    except Exception:
                        try:
                            phone = soup.find('span', {'class': 'icon-phone'}).text.strip()
                        except Exception:
                            phone = ''

            conpany_msg = (shopname, phone, address)
            # 保存数据到csv文件
            r = redis.Redis(host='47.105.174.154', port=6379, db=0)
            had = r.get(phone)
            if (had is None) and (phone != '暂无'):
               r.set(phone, shopname)
               print('店铺名称: %s' % shopname)
               print('联系电话: %s' % phone)
               print('地址: %s' % address)
               save_csv(conpany_msg)
        else:
            return



# 获取地址信息
def get_address(response):
    address_str = re.findall('id="address">(.+?)</span>', response)
    if len(address_str)>0:
        address_str = address_str[0]
    else:
        return False

    address_list = []  # 地址存放的列表
    one_1 = []
    one_2 = []
    head_two = re.sub("<e", "", address_str.split(" ")[1])
    one_1.append("")
    one_1.append(head_two + " ")
    one_2.append(tuple(one_1))
    address_list.append(one_2)
    # 分割，正则来获取所需要的信息
    for i in address_str.split(" "):
        i_str_1 = re.sub("</e>", "", i)
        i_str_2 = re.sub("</d>", "", i_str_1)
        i_str_3 = re.sub(">", "", i_str_2)
        i_str_4 = re.sub("<e", "", i_str_3)
        i_str_5 = re.sub("<d", "", i_str_4)
        re_a = re.findall('class="(.+?)"(.+?)/', i_str_5 + " /")
        address_list.append(re_a)

    address_data_list = []
    for i in address_list:
        if i:
            if i[0][1] != " ":
                address_data_list.append(i[0][0])
                address_data_list.append(i[0][1])
            else:
                address_data_list.append(i[0][0])
    address_content = []
    for i in address_data_list:
        if i.isalnum():
            if 'uj' in i:
                address_content.append(get_text(i))
            else:
                address_content.append(get_digital(i))
        else:
            address_content.append(i.strip(" "))

    return ("".join(address_content))


# 获取电话信息
def get_phone(response):
    phone_str = re.findall('name">电话：</span>(.+?)</p>', response)
    if len(phone_str)>0:
        phone_str = phone_str[0]
    else:
        return False

    on = re.findall('(无) <a', phone_str)
    if on and on[0].strip(" ") == '无':
        return "暂无"
    elif not re.findall('d', phone_str):
        return phone_str
    else:
        phone_list = []
        for i in phone_str.split(" "):
            for j in i.split("</"):
                one_num = re.findall('>(1)|(1)<', j)
                if len(one_num) > 0:
                    if one_num[0][0]:
                        phone_list.append(one_num[0][0])
                    else:
                        phone_list.append(one_num[0][1])

                one_num = re.findall('(-)', j)
                phone_list.append(one_num)
                one_num = re.findall('(11)', j)
                phone_list.append(one_num)
                one_num = re.findall('(111)', j)
                phone_list.append(one_num)
                middle_num = re.findall("(&nbsp;)", j)
                if middle_num:
                    phone_list.append(middle_num)
                re_phone = re.findall('class="(.+?)"', j)
                phone_list.append(re_phone)
        phone_data_list = []

        for i in phone_list:
            if i:
                if i[0] != " ":
                    if i[0] == '&nbsp;':
                        phone_data_list.append("/")
                    else:
                        phone_data_list.append(i[0])
        phone_num = []

        for i in phone_data_list:
            if i.strip(" ") == '1' or i.strip(" ") == "1-" or i.strip(" ") == '/' or i.strip(" ") == '-':
                phone_num.append(i.strip(" "))
            else:
                phone_num.append(get_digital(i))
        return ("".join(phone_num))


# 地址解密
def get_text(id):
    # 获取加密的值的x，y坐标，例如：zogwtn
    re_wqd = re.compile(r"\.%s{background:-(\d+)\.0px -(\d+)\.0px;}" % id)
    time.sleep(0.1)
    wqd = re.findall(re_wqd, one)
    x = wqd[0][0]  # x坐标
    y = wqd[0][1]  # y坐标
    sum_x = int((int(x) / 14))  # 计算x偏移量
    sum_y = round(int(y) / 34)  # 计算y的偏移量
    if sum_y != 0:
        sum_y -= 1
    # print("x轴:{},y轴:{}|x偏移量:{},y偏移量:{}".format(e,f,sum_e,sum_f))
    # 获取到加密的数字组
    url_qfr = "http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/9df4c3894aa345d9949c10eaf18601db.svg"
    response = requests.get(url_qfr, headers=_headers).text
    get_wqd = re.findall(">(.+?)</text>", response)
    wqd_list = []
    for i in get_wqd:
        wqd_list.append(list(i))

    try:
        addrCharArr = wqd_list[sum_y]
    except Exception:
        addrCharArr = wqd_list[sum_y-1]

    if len(addrCharArr) > sum_x:
        addrChar = addrCharArr[sum_x]
    else:
        sum_y = sum_y + 1
        addrChar = wqd_list[sum_y][sum_x]
    return addrChar


# 数字解密
def get_digital(id):
    re_zog = re.compile(r"\.%s{background:-(\d+)\.0px -(\d+)\.0px;}" % id)
    time.sleep(0.1)
    zog = re.findall(re_zog, one)
    if zog:
        x = zog[0][0]
        y = zog[0][1]
        sum_x = int((int(x) / 14))
        sum_y = int(int(y) / 31)
        if sum_y != 0:
            sum_y -= 1
        # print("x轴:{},y轴:{}|x偏移量:{},y偏移量:{}".format(e,f,sum_e,sum_f))
        url_vhk = "http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/dbd16d91d679830e2242660186cbd29c.svg"

        response = requests.get(url_vhk, headers=_headers).text
        get_zog = re.findall(">(.+?)</text>", response)
        zog_list = []
        for i in get_zog:
            zog_list.append(list(i))
        # print(num_list[sum_f][sum_e-1])

        return zog_list[sum_y][sum_x]
    else:
        return '0'


# 主函数，获取企查查中显示的企业页面地址
def main():
    cityList = getCityList()
    cate = open('cate.txt', 'r').read() if os.path.isfile('cate.txt') else '47'
    for i in range(int(cate), len(cityList)):
        if int(cate) != i:
            open('page.txt', 'wb').write(str(1).encode('utf-8'))
        open('cate.txt', 'wb').write(str(i).encode('utf-8'))
        #thread = threading.Thread(target=getShopList,args=(i,))
        #thread.start()
        getShopList(cityList[i])


if __name__ == '__main__':

    # 获取爬虫开始时间
    start_time = datetime.now()
    print('获取大众点评的商家信息')
    print('爬虫开始')
    # csv文件表格的列表头
    '''with open('dazhongdianping.csv', 'a+', newline='', encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv, dialect=('excel'))
        csvwriter.writerow(csv_List_head)'''
    main()
    # 获取爬虫结束时间
    end_time = datetime.now()
    # 获取爬虫花费的时间
    use_time = end_time - start_time
    print('爬虫结束,耗时%s，数据保存在dazhongdianping.csv中' % use_time)
