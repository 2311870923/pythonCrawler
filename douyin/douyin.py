import hashlib, time
import requests
import redis
from datetime import datetime
import os,requests,sys,csv,random,threading,re
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import pyquery

csv_List_head=('抖音ID', '昵称','性别','简介')

#保存数据到csv文件
def save_csv(msg):
    with open('douyin.csv','a',newline='',encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(msg)

'''def getIp():
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
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    if html:
        doc = pyquery.PyQuery(html, parser="html")
        for item in doc("tbody tr").items():
            ipPort = item("td:nth-child(1)").text().replace('\n', '').replace('\r', '')
            schema = item("td:nth-child(3) a").text()
            #ipList.append("{}://{}".format(schema.lower(), ipPort))
            ipitem = "{}://{}".format('http', ipPort)
            proxiesItem = {'http': ipitem, 'https': ipitem}
            try:
                requests.get('https://jokeai.zongcaihao.com/douyin/v292/feed', headers=headers, proxies=proxiesItem, timeout=6)
                proxies = proxiesItem
                break
            except Exception:
                print(proxiesItem)
                continue
    driver.quit()
    return proxies'''
def getIp():
    ipUrl = "http://127.0.0.1:9999/pop"
    req = requests.get(ipUrl)
    ipJson = req.json()
    proxies = {}
    for i in ipJson:
        if i=='http':
            proxies['http'] = ipJson[i]
            proxies['https'] = ipJson[i]
        else:
            proxies['http'] = ipJson[i].replace('https', 'http')
            proxies['https'] = ipJson[i].replace('https', 'http')
    return proxies


def getList():
    #paramsUrl = "https://aweme.snssdk.com/aweme/v1/feed/?app_type=normal&manifest_version_code=290&_rticket=1550930244608&ac=wifi&device_id=66294943700&iid=64323608375&os_version=9&channel=wandoujia_zhiwei&version_code=290&device_type=ONEPLUS%20A6010&language=zh&uuid=869386044722596&resolution=1080*2261&openudid=89ca1c64a055844d&update_version_code=2902&app_name=aweme&version_name=2.9.0&os_api=28&device_brand=OnePlus&ssmix=a&device_platform=android&dpi=420&aid=1128&count=6&type=0&max_cursor=0&min_cursor=-1&pull_type=2"

    #realUrl = get_feed_url(paramsUrl)
    #realUrl = 'https://jokeai.zongcaihao.com/douyin/v292/feed'
    realUrl = 'http://111.231.195.210/feed/'

    headers = {
        'authority': "jokeai.zongcaihao.com",
        'path': "/douyin/v292/feed",
        'scheme': 'https',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }

    '''proxies = {
        'http': 'http://117.95.31.29:4273',
        'https': 'http://117.95.31.29:4273'
    }'''
    proxies = getIp()
    #cookies_str = "__cfduid = d50d67c0b6d7fe22195ef6e5c4591420b1554888351"
    cookies_str = 'sessionid=yxmjg1sjxsq64pbv3f1wl2js9bq56zcd'
    cookies = {i.split('=')[0]:i.split('=')[1] for i in cookies_str.split('; ')}
    #print(proxies)
    try:
        req = requests.get(realUrl, headers=headers, cookies=cookies, proxies=proxies, timeout=6.0)
        req.encoding = 'utf8'
        print(req.text)
    except Exception:
        print(Exception)
        print("bbb")
        return

    #print(req.text)
    try:
        print("aaa")
        infoList = req.json()['data']['aweme_list']
        print(infoList)
    except Exception:
        return
    for info in infoList:
        name = info['author']['nickname']
        brief = info['author']['signature']
        id = info['author']['uid']
        did = info['author']['short_id']
        unid= info['author']['unique_id']
        if not unid:
            unid = did
        sex = info['author']['gender']
        if sex == 1:
            sex = '男'
        else:
            sex = '女'
        had = r.get('douyinid-' + str(id))
        user_msg = (unid, name, sex, brief)
        pattern = re.compile('[A-Z]+|[a-z]+|[0-9]]+')
        match = pattern.findall(brief)
        print(brief)
        if (had is None) and brief and len(match) > 0:
            r.set('douyinid-' + str(id), id)
            print('用户ID: %s' % id)
            print('用户抖音ID: %s' % unid)
            print('用户名: %s' % name)
            print('性别: %s' % sex)
            print('简介: %s' % brief)
            save_csv(user_msg)

def get_feed_url(paramsUrl):  # 获取带有加密参数的url
    headers = {
        "User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)",
    }
    form_data = {
        'url': "https://aweme.snssdk.com/aweme/v1/feed/?app_type=normal&manifest_version_code=290&_rticket=1550930244608&ac=wifi&device_id=66294943700&iid=64323608375&os_version=9&channel=wandoujia_zhiwei&version_code=290&device_type=ONEPLUS%20A6010&language=zh&uuid=869386044722596&resolution=1080*2261&openudid=89ca1c64a055844d&update_version_code=2902&app_name=aweme&version_name=2.9.0&os_api=28&device_brand=OnePlus&ssmix=a&device_platform=android&dpi=420&aid=1128&count=6&type=0&max_cursor=0&min_cursor=-1&pull_type=2"
    }
    print('未带加密参数url:', form_data)
    proxies = {
        'http': "http://117.131.235.198:8060"
    }
    try:
        feed_url = requests.post('http://jokeai.zongcaihao.com/douyin/v292/sign', data=form_data, headers=headers, proxies=proxies).json()['url']
        print('带有加密参数的完整url:', feed_url)
    except Exception as e:
        feed_url = None
        print('get_sign_url() error:', str(e))
    return feed_url

def main():
    while True:
        getList()
        #time.sleep(6)

if __name__ == '__main__':
    r = redis.Redis(host='47.105.174.154', port=6379,db=0)
    # 获取爬虫开始时间
    start_time = datetime.now()
    print ('获取快手用户信息')
    print ('爬虫开始')
    # csv文件表格的列表头
    '''with open('douyin.csv','a+',newline='',encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(csv_List_head)'''
    for i in range(0, 40):
        thread = threading.Thread(target=main)
        thread.start()
    #main()
    # 获取爬虫结束时间
    end_time = datetime.now()
    # 获取爬虫花费的时间
    use_time = end_time - start_time
    print ('爬虫结束,耗时%s，数据保存在douyin.csv中' % use_time)
