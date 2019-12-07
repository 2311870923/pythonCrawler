#!/usr/bin/env python3
# coding=gbk

import os,requests,sys,csv,time,random,threading,re
from bs4 import BeautifulSoup
import pyquery
from datetime import datetime
import math
import urllib3.contrib.pyopenssl
import redis
import json

# 行业列表
base_url = 'https://s.hc360.com/company/search.html?kwd=&z={area}&pnum={page}'
# 请求头
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
    'Connection': 'close',
}

# csv的列表头
csv_List_head=('企业名称','联系人','联系电话','联系手机','地址','官网')

def getAllCategory():
    provList = [{'name': '华北', 'province': ['北京', '天津', '河北省', '山西省', '内蒙古自治区'], 'city': [[], [], ['石家庄市', '保定市', '沧州市', '廊坊市', '唐山市', '邢台市', '邯郸市', '衡水市', '秦皇岛市', '张家口市', '承德市'], ['太原市', '运城市', '临汾市', '大同市', '长治市', '晋城市', '吕梁市', '阳泉市', '忻州市', '朔州市', '晋中市'], ['呼和浩特市', '包头市', '赤峰市', '呼伦贝尔市', '通辽市', '鄂尔多斯市', '巴彦淖尔盟市', '锡林郭勒盟', '乌兰察布市', '兴安盟', '乌海市', '阿拉善盟市']]}, {'name': '东北', 'province': ['辽宁省', '吉林省', '黑龙江省'], 'city': [['沈阳市', '大连市', '鞍山市', '锦州市', '营口市', '丹东市', '抚顺市', '朝阳市', '葫芦岛市', '铁岭市', '辽阳市', '盘锦市', '阜新市', '本溪市'], ['长春市', '吉林市', '延边朝鲜族自治州', '通化市', '四平市', '白城市', '松原市', '白山市', '辽源市'], ['哈尔滨市', '大庆市', '齐齐哈尔市', '佳木斯市', '伊春市', '牡丹江市', '鸡西市', '黑河市', '绥化市', '双鸭山市', '鹤岗市', '七台河市', '大兴安岭地区']]}, {'name': '华东', 'province': ['上海', '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省'], 'city': [[], ['苏州市', '南京市', '无锡市', '常州市', '徐州市', '南通市', '扬州市', '泰州市', '盐城市', '镇江市', '连云港市', '淮安市', '宿迁市'], ['杭州市', '温州市', '宁波市', '金华市', '台州市', '嘉兴市', '绍兴市', '湖州市', '丽水市', '衢州市', '舟山市'], ['合肥市', '淮北市', '安庆市', '芜湖市', '阜阳市', '滁州市', '蚌埠市', '马鞍山市', '六安市', '巢湖市', '宣城市', '淮南市', '毫州市', '黄山市', '池州市', '铜陵市', '宿州市'], ['厦门市', '泉州市', '福州市', '漳州市', '莆田市', '龙岩市', '宁德市', '三明市', '南平市'], ['南昌市', '抚州市', '赣州市', '九江市', '上饶市', '吉安市', '景德镇市', '萍乡市', '新余市', '宜春市', '鹰潭市'], ['济南市', '青岛市', '淄博市', '枣庄市', '东营市', '烟台市', '莱阳市', '潍坊市', '济宁市', '泰安市', '威海市', '日照市', '滨州市', '德州市', '聊城市', '临沂市', '菏泽市', '莱芜市']]}, {'name': '中南', 'province': ['河南省', '湖北省', '湖南省', '广东省', '广西省', '海南省'], 'city': [['郑州市', '洛阳市', '新乡市', '南阳市', '安阳市', '焦作市', '许昌市', '商丘市', '平顶山市', '周口市', '信阳市', '濮阳市', '开封市', '驻马店市', '鹤壁市', '三门峡市', '漯河市', '济源市'], ['武汉市', '襄樊市', '宜昌市', '荆州市', '十堰市', '孝感市', '黄冈市', '恩施土家族苗族自治州', '黄石市', '荆门市', '随州市', '咸宁市', '鄂州市', '潜江市', '神农架林区市', '天门市', '仙桃市'], ['长沙市', '湘潭市', '衡阳市', '株洲市', '郴州市', '常德市', '邵阳市', '岳阳市', '怀化市', '永州市', '娄底市', '益阳市', '湘西土家族苗族自治州', '张家界市'], ['深圳市', '广州市', '东莞市', '佛山市', '中山市', '惠州市', '珠海市', '汕头市', '江门市', '肇庆市', '揭阳市', '梅州市', '茂名市', '潮州市', '清远市', '韶关市', '湛江市', '河源市', '汕尾市', '云浮市', '阳江市'], ['南宁市', '桂林市', '柳州市', '玉林市', '贵港市', '百色市', '梧州市', '北海市', '钦州市', '河池市', '防城港市', '来宾市', '贺州市', '崇左市'], ['海口市', '三亚市', '白沙黎族自治县', '屯昌县市', '五指山市', '文昌市', '澄迈县', '东方市', '万宁市', '琼海市', '定安县', '保亭黎族苗族自治县', '昌江黎族自治县', '琼中黎族苗族自治县', '临高县', '乐东黎族自治县', '陵水黎族自治县', '儋州']]}, {'name': '西南', 'province': ['重庆', '四川省', '贵州省', '云南省', '西藏自治区'], 'city': [[], ['成都市', '绵阳市', '德阳市', '南充市', '宜宾市', '乐山市', '泸州市', '达州市', '自贡市', '广元市', '凉山彝族自治州', '广安市', '内江市', '攀枝花市', '遂宁市', '眉山市', '资阳市', '巴中市', '雅安市', '阿坝藏族羌族自治州', '甘孜藏族自治州'], ['贵阳市', '遵义市', '黔东南苗族侗族自治州', '黔西南布依族苗族自治州', '毕节地区', '六盘水市', '铜仁地区', '黔南布依族苗族自治州', '安顺市'], ['昆明市', '文山壮族苗族自治州', '保山市', '曲靖市', '玉溪市', '大理白族自治州', '西双版纳傣族自治州', '昭通市', '楚雄彝族自治州', '丽江市', '德宏傣族景颇族自治州', '迪庆藏族自治州', '红河哈尼族彝族自治州', '临沧市', '怒江傈傈族自治州', '普洱市'], ['拉萨市', '阿里市', '昌都市', '那曲市', '林芝市', '日喀则市', '山南市']]}, {'name': '西北', 'province': ['陕西省', '甘肃省', '青海省', '宁夏回族自治区', '新疆维吾尔自治区'], 'city': [['西安市', '榆林市', '宝鸡市', '汉中市', '咸阳市', '渭南市', '延安市', '安康市', '商洛市', '铜川市'], ['兰州市', '白银市', '天水市', '酒泉市', '庆阳市', '平凉市', '张掖市', '武威市', '陇南市', '定西市', '临夏回族自治州', '金昌市', '嘉峪关市', '甘南藏族自治州'], ['西宁市', '海北藏族自治州', '果洛藏族自治州', '海南藏族子自治州', '海东市', '海西蒙古族藏族自治州', '玉树藏族自治州', '黄南藏族自治州'], ['银川市', '石嘴山市', '吴忠市', '固原市', '中卫市'], ['乌鲁木齐市', '喀什地区', '巴音郭楞蒙古自治州', '伊犁哈萨克自治州', '阿克苏地区', '昌吉市', '哈密地区', '和田地区', '吐鲁番地区', '阿拉尔市', '博尔塔拉蒙古自治州', '昌吉回族自治州', '克拉玛依市', '克孜勒苏柯尔克孜自治州', '石河子市', '图木舒克市', '五家渠市']]}]

    areaArr = []
    for prov in provList:
       for i in range(0, len(prov['city'])):
            area = "中国:" + prov['province'][i]
            if len(prov['city'][i]) > 0:
                for c in prov['city'][i]:
                    areaCity = area + ":" + c
                    areaArr.append(areaCity)
            else:
                areaArr.append(area)
    print(areaArr)
    exit()
    return areaArr


def getDetailInfo(detailUrl, shopName):
    #tnum = random.randint(1, 2)
    '''tnum = 0.5
    print('防止网站禁止爬虫，等待%s秒' % tnum)
    time.sleep(tnum)'''
    print(detailUrl)
    '''tnum = random.randint(2, 5)
    print('防止网站禁止爬虫，等待%s秒' % tnum)
    time.sleep(tnum)'''
    requests.adapters.DEFAULT_RETRIES = 50
    requests.packages.urllib3.disable_warnings()
    s = requests.session()
    s.keep_alive = False
    try:
        req = requests.get(detailUrl, headers=headers, timeout=6.0, verify=False)
    except Exception:
        return
    soup = BeautifulSoup(req.text, "html.parser")
    try:
        leftArr = soup.find('div', {'class': 'ContacCon3'}).find('ul').findAll('div', {'class': 'con3Left'})
    except Exception:
        return
    rightArr   = soup.find('div', {'class': 'ContacCon3'}).find('ul').findAll('div', {'class': 'con3Rig'})

    people = ''
    phone = ''
    mobile = ''
    address = ''
    web = ''
    for i in range(0, len(leftArr)):
        infoItem = leftArr[i].find('span')
        if infoItem.text == '联系人':
            people = rightArr[i].find('span').find('a').text.strip()
        if infoItem.text == '电话':
            phone = rightArr[i].text.strip()
        if infoItem.text == '手机':
            mobile = rightArr[i].text.strip()
        if infoItem.text == '官网':
            web = rightArr[i].find('a').text.strip()
        if infoItem.text == '地址':
            address = rightArr[i].text.strip()

    if "**" in phone:
        try:
            leftArr = soup.find('div', {'class': 'ContactBox'}).find('ul').findAll('li')
        except Exception:
            return
        for left in leftArr:
            infoItem = left.findAll('span')
            if infoItem[0].text == '电话':
                phone = infoItem[1].text.strip("：")
    if "**" in mobile:
        try:
            leftArr = soup.find('div', {'class': 'ContactBox'}).find('ul').findAll('li')
        except Exception:
            return
        for left in leftArr:
            infoItem = left.findAll('span')
            if infoItem[0].text == '手机':
                mobile = infoItem[1].text.strip("：")

    conpany_msg = (shopName, people, phone, mobile, web, address)
    had = r.get(mobile+' '+phone)
    if (phone or mobile) and (had is None):
        r.set(mobile+' '+phone, shopName)
        print('企业名称: %s' % shopName)
        print('联系人: %s' % people)
        print('联系电话: %s' % phone)
        print('联系手机: %s' % mobile)
        print('地址: %s' % address)
        print('官网: %s' % web)
        save_csv(conpany_msg)
    else:
        print('手机号'+mobile+' '+phone)

#保存数据到csv文件
def save_csv(msg):
    with open('huichong.csv','a',newline='',encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(msg)

def getCompanyList(area, i):
    url = base_url.format(area=area, page=1)
    print(url)
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.text, "html.parser")
    total = soup.find('span', {'class': 'total'}).text.strip()
    pageCount = int(total[1:-1])
    start_page = open('page.txt', 'r').read() if os.path.isfile('page.txt') else '6'
    for page in range(int(start_page), pageCount+1):
        open('page.txt', 'wb').write(str(page).encode('utf-8'))
        print("第"+str(page)+"页")
        url = base_url.format(area=area, page=page)
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.text, "html.parser")
        contactLinkList = soup.find_all('dt', {'class': 'til'})
        for contactLink in contactLinkList:
            detailUrl = contactLink.find('h3').find('a').get('href')
            detailUrl = detailUrl + 'shop/company.html'
            shopName = contactLink.find('h3').find('a').text.strip()
            getDetailInfo(detailUrl, shopName)


# 主函数
def main():
    areaList = getAllCategory()  #362
    #getCompanyList(areaList[0])
    cate = open('cate.txt', 'r').read() if os.path.isfile('cate.txt') else '55'
    for i in range(int(cate), len(areaList)):
        if int(cate) != i:
            open('page.txt', 'wb').write(str(1).encode('utf-8'))
        open('cate.txt', 'wb').write(str(i).encode('utf-8'))
        print("第"+str(i)+"个分类")
        getCompanyList(areaList[i], i)
        #thread = threading.Thread(target=getCompanyList,args=(areaList[i], i,))
        #thread.start()


if __name__ == '__main__':
    r = redis.Redis(host='47.105.174.154', port=6379,db=0)
    # 获取爬虫开始时间
    start_time = datetime.now()
    print ('获取慧聪网的企业信息')
    print ('爬虫开始')
    # csv文件表格的列表头
    with open('huichong.csv','a+',newline='',encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(csv_List_head)
    main()
    # 获取爬虫结束时间
    end_time = datetime.now()
    # 获取爬虫花费的时间
    use_time = end_time - start_time
    print ('爬虫结束,耗时%s，数据保存在huichong.csv中' % use_time)