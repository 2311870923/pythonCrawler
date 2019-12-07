#!/usr/bin/env python3

import os,requests,sys,csv,time,random,threading,re
from bs4 import BeautifulSoup
import pyquery
from datetime import datetime
import math
import redis
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

# 行业列表
base_url = 'http://www.cnlinfo.net/company/index.htm'
# 请求头
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
}

# csv的列表头
csv_List_head=('企业名称','联系人','联系电话','联系手机','地址','邮箱')

def getAllCategory():
    req = requests.get(base_url, headers=headers, proxies=getIp())
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text, "html.parser")
    dlList = soup.find_all('dl', {'class': 'cat_box'})
    linkList = []
    for dl in dlList:
        ddList = dl.find_all('dd')
        for dd in ddList:
            aaList = dd.find_all('a')
            for aa in aaList:
                linkList.append(aa.get('href'))

    return linkList

def getDetailInfo(detailUrl, shopName):
    print(detailUrl)
    '''tnum = random.randint(2, 5)
    print('防止网站禁止爬虫，等待%s秒' % tnum)
    time.sleep(tnum)'''
    req = requests.get(detailUrl, headers=headers, proxies=getIp())
    soup = BeautifulSoup(req.text, "html.parser")
    try:
        infoArr = soup.find('ul', {'class': 'lianxi-fangshi-list'}).findAll('li')
    except Exception:
        try:
            infoArr = soup.find('div', {'class': 'gs-lxwm'}).find('ul').findAll('li')
        except Exception:
            req = requests.get(detailUrl, headers=headers)
            soup = BeautifulSoup(req.text, "html.parser")
            try:
                infoArr = soup.find('ul', {'class': 'lianxi-fangshi-list'}).findAll('li')
            except Exception:
                infoArr = soup.find('div', {'class': 'gs-lxwm'}).find('ul').findAll('li')

    try:
        mobile = soup.find('div', {'class': 'dialog-phone'}).text.strip()
    except Exception:
        mobile = ''
    people = ''
    phone = ''
    address = ''
    email = ''
    for info in infoArr:
        infoItem = info.findAll('span')
        if infoItem[0].text == '联系人：':
            people = infoItem[1].text.strip()
        if infoItem[0].text == '联系电话：':
            phone = infoItem[1].text.strip()
        if infoItem[0].text == '公司地址：':
            address = infoItem[1].text.strip()
        if infoItem[0].text == 'E-mail：':
            email = infoItem[1].text.strip()
    conpany_msg = (shopName, people, phone, mobile, address, email)
    had = r.get(mobile+' '+phone)
    if (phone or mobile) and (had is None):
        r.set(mobile+' '+phone, shopName)
        print('企业名称: %s' % shopName)
        print('联系人: %s' % people)
        print('联系电话: %s' % phone)
        print('联系手机: %s' % mobile)
        print('地址: %s' % address)
        print('邮箱: %s' % email)
        save_csv(conpany_msg)

#保存数据到csv文件
def save_csv(msg):
    with open('hangyexinxi.csv','a',newline='',encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(msg)

def getCompanyList(link, ipage):
    req = requests.get(link, headers=headers, proxies=getIp())
    soup = BeautifulSoup(req.text, "html.parser")
    total = soup.find('span', {'class': 'slNum'}).find('b').text.strip()
    pageCount = int(math.ceil(int(total)/36))
    link = link[:-4]
    start_page = 1
    if ipage == 0:
        start_page = 5
    for page in range(start_page, pageCount+1):
        print("第"+str(page)+"页")
        realLink = link+"_p"+str(page)+".htm"
        req = requests.get(realLink, headers=headers, proxies=getIp())
        soup = BeautifulSoup(req.text, "html.parser")
        contactLinkList = soup.find_all('div', {'class': 'com_info'})
        for contactLink in contactLinkList:
            detailUrl = contactLink.find('span', {'class': 'contact_style'}).find('a').get('href')
            shopName = contactLink.find('h2').find('a').text.strip()
            getDetailInfo(detailUrl, shopName)


def getIp():
    """
            goubanjia 代理：http://www.goubanjia.com
            """
    url = "http://www.goubanjia.com/"
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    # options.setCapability(CapabilityType.ACCEPT_SSL_CERTS, true)
    # options.setCapability(CapabilityType.ACCEPT_INSECURE_CERTS, true)
    driver = Chrome(executable_path='/Users/echo/Documents/sites/wxhub-master/chromedriver', chrome_options=options)
    driver.get(url)
    html = driver.page_source
    html_compile = re.compile(r'<p style="display:.*?none;">.*?<\/p>')  # >匹配IP
    html = re.sub(html_compile, '', html)  # 获取所有IP
    ipList = []
    proxies = None
    if html:
        doc = pyquery.PyQuery(html, parser="html")
        for item in doc("tbody tr").items():
            ipPort = item("td:nth-child(1)").text().replace('\n', '').replace('\r', '')
            schema = item("td:nth-child(3) a").text()
            #ipList.append("{}://{}".format(schema.lower(), ipPort))
            ipitem = "{}://{}".format(schema.lower(), ipPort)
            proxiesItem = {'http': ipitem}
            try:
                requests.get(base_url, headers=headers, proxies=proxiesItem, timeout=3)
                proxies = proxiesItem
            except Exception:
                print(proxiesItem)
                continue
    return proxies
    #tnum = random.randint(0, len(ipList)-1)
    #return ipList[tnum]

# 主函数
def main():
    linkList = getAllCategory()
    #getCompanyList(linkList[0])
    for i in range(0, len(linkList)):
        print("第"+str(i)+"个分类")
        getCompanyList(linkList[0], i)
        #thread = threading.Thread(target=getCompanyList,args=(link,))
        #thread.start()


if __name__ == '__main__':
    r = redis.Redis(host='127.0.0.1', port=6379,db=0)
    # 获取爬虫开始时间
    start_time = datetime.now()
    print ('获取中国行业信息网的企业信息')
    print ('爬虫开始')
    # csv文件表格的列表头
    '''with open('hangyexinxi.csv','a+',newline='',encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(csv_List_head)'''
    main()
    # 获取爬虫结束时间
    end_time = datetime.now()
    # 获取爬虫花费的时间
    use_time = end_time - start_time
    print ('爬虫结束,耗时%s，数据保存在hangyexinxi.csv中' % use_time)