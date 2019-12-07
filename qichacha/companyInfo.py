#!/usr/bin/env python3

import os,requests,sys,csv,time,random
from bs4 import BeautifulSoup
from datetime import datetime
import redis

# 企查查广东地区的页面列表地址
base_url = 'https://www.qichacha.com/{area}_{pagenum}.html'
# 企查查网站地址，用于补全获取的URL地址
head_url = 'https://www.qichacha.com'
# 请求头
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
}

# cookies 通过登录网站可以获取 以字典形式保存
# cookies = {}

# csv的列表头
csv_List_head=('企业名称','法定代表人','联系电话','邮箱地址','官方网站','企业地址')


#保存数据到csv文件
def save_csv(msg):
    with open('qichacha_company.csv','a',newline='',encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(msg)


# 获取页面内容
def contentPage(url):
    url = url
    # 获取完整的电话号码和邮箱地址，请在requets.get()中添加cookies=cookies
    #15737135239
    #cookies_str = 'UM_distinctid=169e286201041d-06a03135208267-12366d57-1fa400-169e2862011476; zg_did=%7B%22did%22%3A%20%22169e28620d3275-075e030ec5f2ab-12366d57-1fa400-169e28620d43f0%22%7D; _uab_collina=155428363496833536856398; acw_tc=2a30794915542836350281307e8e70c04c17fd95e393861d7dd2d952e1; QCCSESSID=vqm5d84g2nlakd7qv3tk0dnio3; hasShow=1; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1554704152,1554907059,1555040487,1555125501; CNZZDATA1254842228=582116660-1554282401-https%253A%252F%252Fwww.baidu.com%252F%7C1555130964; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201555132447872%2C%22updated%22%3A%201555132488078%2C%22info%22%3A%201554893073030%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.qichacha.com%22%2C%22cuid%22%3A%20%2219a38127089b5750cfe8cdb0586853f3%22%7D; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1555132488'
    #18790648259
    cookies_str = 'UM_distinctid=169e286201041d-06a03135208267-12366d57-1fa400-169e2862011476; zg_did=%7B%22did%22%3A%20%22169e28620d3275-075e030ec5f2ab-12366d57-1fa400-169e28620d43f0%22%7D; _uab_collina=155428363496833536856398; acw_tc=2a30794915542836350281307e8e70c04c17fd95e393861d7dd2d952e1; QCCSESSID=vqm5d84g2nlakd7qv3tk0dnio3; hasShow=1; CNZZDATA1254842228=582116660-1554282401-https%253A%252F%252Fwww.baidu.com%252F%7C1555155602; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1554907059,1555040487,1555125501,1555156245; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201555156245163%2C%22updated%22%3A%201555156290502%2C%22info%22%3A%201554893073030%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.baidu.com%22%2C%22cuid%22%3A%20%223d102e7ed038fc41b666a0740f02d3a2%22%7D; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1555156291'
    #17124267519
    #cookies_str = 'UM_distinctid=169e286201041d-06a03135208267-12366d57-1fa400-169e2862011476; zg_did=%7B%22did%22%3A%20%22169e28620d3275-075e030ec5f2ab-12366d57-1fa400-169e28620d43f0%22%7D; _uab_collina=155428363496833536856398; acw_tc=2a30794915542836350281307e8e70c04c17fd95e393861d7dd2d952e1; QCCSESSID=vqm5d84g2nlakd7qv3tk0dnio3; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1554283635,1554624696,1554704152; CNZZDATA1254842228=582116660-1554282401-https%253A%252F%252Fwww.baidu.com%252F%7C1554790190; hasShow=1; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201554792824836%2C%22updated%22%3A%201554792919790%2C%22info%22%3A%201554283634915%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.qichacha.com%22%2C%22cuid%22%3A%20%222bab46d79a2dfb1e47d4ea730d647397%22%7D; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1554792920'
    #17124267526
    #cookies_str = 'UM_distinctid=169e286201041d-06a03135208267-12366d57-1fa400-169e2862011476; zg_did=%7B%22did%22%3A%20%22169e28620d3275-075e030ec5f2ab-12366d57-1fa400-169e28620d43f0%22%7D; _uab_collina=155428363496833536856398; acw_tc=2a30794915542836350281307e8e70c04c17fd95e393861d7dd2d952e1; QCCSESSID=vqm5d84g2nlakd7qv3tk0dnio3; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1554624696,1554704152,1554907059,1555040487; CNZZDATA1254842228=582116660-1554282401-https%253A%252F%252Fwww.baidu.com%252F%7C1555060295; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201555061715711%2C%22updated%22%3A%201555062506084%2C%22info%22%3A%201554893073030%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22%22%2C%22cuid%22%3A%20%22aaf7cdb0cf64d7fc59820a7b3c7a4836%22%7D; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1555062506'
    cookies = {i.split('=')[0]:i.split('=')[1] for i in cookies_str.split('; ')}
    try:
        req = requests.get(url,headers=headers,cookies=cookies)
    except Exception as e:
        return
    #print(req.text)
    #exit()    
    soup = BeautifulSoup(req.text,"html.parser")
    [s.extract() for s in soup.findAll('li', {'class': 'dropdown msg-drop'})]
    email = ''
    tel = ''
    web = ''
    address = ''
    # 判断网站是否正常打开
    if req.status_code == 200 :
        # 获取公司名
        try:
            conpanyname = soup.find('div',{'class':'row title jk-tip'}).h1.text.strip()
            #conpanyname = soup.find('div')
        except AttributeError:
            conpanyname = soup.find('div',{'class':'row title'}).h1.text.strip()
            #sys.exit('获取不了目标页面内容,爬虫自动退出,请检查目标页面是否正常打开或者自动跳转到首页')
        # 获取电话、邮箱、官网、公司地址信息
        row = soup.find('div',{'class':'content'}).find_all('div',{'class':'row'})
        for i in row:
            # 判断是否i.find('span',{'class':'cdes'})有内容
            if i.find('span',{'class':'cdes'}):
                # 判断获取的i.find('span',{'class':'cdes'})是否为电话
                if i.find('span',{'class':'cdes'}).text.strip() == '电话：':
                    try:
                        tel = i.find('span',{'class':'cvlu'}).span.text.strip()
                    except AttributeError:
                        tel = i.find('span',{'class':'cvlu'}).text.strip()
                    # 获取官网
                    if i.find('span',{'class':'cdes'}).find_parent().find_next_sibling().text.strip() == '官网：':
                        try:
                            web = i.find('span',{'class':'cdes'}).find_parent().find_next_sibling().find_next('span').find('a').text.strip()
                        except AttributeError:
                            web = i.find('span',{'class':'cdes'}).find_parent().find_next_sibling().find_next('span').text.strip()
                # 判断获取的i.find('span',{'class':'cdes'})是否为邮箱
                if i.find('span',{'class':'cdes'}).text.strip() == '邮箱：':
                    try:
                        email = i.find('span',{'class':'cvlu'}).text.strip()
                    except AttributeError:
                        email = '暂无'
                    # 获取地址
                    if i.find('span',{'class':'cdes'}).find_parent().find_next_sibling().text.strip() == '地址：':
                        try:
                            address = i.find('span',{'class':'cdes'}).find_parent().find_next_sibling().find_next('span').a.text.strip()                
                        except AttributeError:
                            address = i.find('span',{'class':'cdes'}).find_parent().find_next_sibling().find_next('span').text.strip()

        # 获取公司法人名称
        try:
            legal_person = soup.find('div',{'class':'boss-td'}).find('a',{'class':'bname'}).text.strip()
        except AttributeError:
            legal_person = ''
            pass
            #legal_person = soup.find('div',{'class':'boss-td'}).find('a',{'class':'bcom'}).text.strip()
        
        # 获取公司的注册相关信息，通过定位table获取
        tablemsg = soup.find('table',{'class':'ntable'}).find_next('table').find_all('tr')

        '''for tr in tablemsg:
            # 判断每个tr中第一个td内容获取相关内容，同一个td的其他内容通过find_next()定位
            if tr.td.text.strip() == '注册资本：':
                Registered_capital = tr.td.find_next('td').text.strip()
                Paid_capital = tr.td.find_next('td').find_next('td').find_next('td').text.strip()
            if tr.td.text.strip() == '经营状态：':
                Operating_state = tr.td.find_next('td').text.strip()
                Date_of_establishment = tr.td.find_next('td').find_next('td').find_next('td').text.strip()
            if tr.td.text.strip() == '统一社会信用代码：':
                Usc_code = tr.td.find_next('td').text.strip()
                Tid_number = tr.td.find_next('td').find_next('td').find_next('td').text.strip()
            if tr.td.text.strip() == '注册号：':
                Registration_number = tr.td.find_next('td').text.strip()
                Organization_Code = tr.td.find_next('td').find_next('td').find_next('td').text.strip()
            if tr.td.text.strip() == '公司类型：':
                Type_of_company = tr.td.find_next('td').text.strip()
                Industry = tr.td.find_next('td').find_next('td').find_next('td').text.strip()
            if tr.td.text.strip() == '核准日期：':
                Date_of_approval = tr.td.find_next('td').text.strip()
                Registration_authority = tr.td.find_next('td').find_next('td').find_next('td').text.strip()
            if tr.td.text.strip() == '所属地区：':
                Area = tr.td.find_next('td').text.strip()
            if tr.td.text.strip() == '曾用名':
                Name_used_before = tr.td.find_next('td').text.strip()
                Operation_mode = tr.td.find_next('td').find_next('td').find_next('td').text.strip()
            if tr.td.text.strip() == '人员规模':
                Personnel_scale = tr.td.find_next('td').text.strip()
                Time_limit_for_business = tr.td.find_next('td').find_next('td').find_next('td').text.strip()
            if tr.td.text.strip() == '经营范围：':
                Scope_of_operation = tr.td.find_next('td').text.strip()'''

        '''print ('企业名称: %s' % conpanyname)
        print ('曾用名: %s ' % Name_used_before)
        print ('法定代表人: %s' % legal_person)
        print ('联系电话: %s' % tel)
        print ('邮箱地址: %s' % email)
        print ('官方网站: %s' % web)
        print ('企业地址: %s' % address)'''

        '''print ('所属行业: %s ' % Industry)
        print ('公司类型: %s ' % Type_of_company)
        print ('经营状态: %s ' % Operating_state)
        print ('经营方式: %s ' % Operation_mode)
        print ('人员规模: %s ' % Personnel_scale)
        print ('所属地区: %s ' % Area)
        print ('营业期限: %s ' % Time_limit_for_business)
        print ('经营范围: %s ' % Scope_of_operation)'''

        '''print ('注册资本: %s' % Registered_capital)
        print ('实缴资本: %s ' % Paid_capital)
        print ('成立日期: %s ' % Date_of_establishment)
        print ('核准日期: %s ' % Date_of_approval)
        print ('登记机关: %s ' % Registration_authority)
        print ('统一社会信用代码: %s ' % Usc_code)
        print ('纳税人识别号: %s ' % Tid_number)
        print ('注册号: %s ' % Registration_number)
        print ('组织机构代码: %s ' % Organization_Code)'''
        #print ('\n')

        # 获取的企业信息
        #Usc_code = "'" + Usc_code
        #Tid_number = "'" + Tid_number
        #Registration_number = "'" + Registration_number

        '''conpany_msg = (conpanyname,Name_used_before,legal_person,tel,email,web,
            address,Industry,Type_of_company,Operating_state,Operation_mode,
            Personnel_scale,Area,Time_limit_for_business,Scope_of_operation,
            Registered_capital,Paid_capital,Date_of_establishment,Date_of_approval,
            Registration_authority,Usc_code,Tid_number,
            Registration_number,Organization_Code)'''
        '''conpany_msg = (conpanyname,Name_used_before,legal_person,tel,email,web,
        address,Industry,Type_of_company,Operating_state,Operation_mode,
        Personnel_scale,Area,Time_limit_for_business,Scope_of_operation)'''
        conpany_msg = (conpanyname,legal_person,tel,email,web,address)
        had = r.get(tel)
        # 保存数据到csv文件
        if (tel != '暂无' or web != '暂无') and (had is None) and ('*' not in tel) and ('*' not in web):
            r.set(tel, conpanyname) 
            print ('企业名称: %s' % conpanyname)
            print ('法定代表人: %s' % legal_person)
            print ('联系电话: %s' % tel)
            print ('邮箱地址: %s' % email)
            print ('官方网站: %s' % web)
            print ('企业地址: %s' % address)
            print ('\n')
            save_csv(conpany_msg)
    else:
        sys.exit('网站打开异常，爬虫自动退出.')


# 主函数，获取企查查中显示的企业页面地址
def main():
    areaArr = ['g_AH', 'g_BJ', 'g_CQ', 'g_FJ', 'g_GS', 'g_GD', 'g_GX', 'g_GZ', 'g_HAIN', 'g_HB', 'g_HLJ', 'g_HEN', 'g_HUB', 'g_HUN', 'g_JS', 'g_JX', 'g_JL', 'g_LN', 'g_NMG', 'g_NX', 'g_QH', 'g_SD', 'g_SH', 'g_SX', 'g_SAX', 'g_SC', 'g_TJ', 'g_XJ', 'g_XZ', 'g_YN', 'g_ZJ', 'g_CN']
    #areaArr = ['g_GS', 'g_GD', 'g_GX', 'g_GZ', 'g_HAIN', 'g_HB', 'g_HLJ', 'g_HEN', 'g_HUB', 'g_HUN', 'g_JS', 'g_JX', 'g_JL', 'g_LN', 'g_NMG', 'g_NX', 'g_QH', 'g_SD', 'g_SH', 'g_SX', 'g_SAX', 'g_SC', 'g_TJ', 'g_XJ', 'g_XZ', 'g_YN', 'g_ZJ', 'g_CN']
    #areaArr = ['g_GX', 'g_GZ', 'g_HAIN', 'g_HB', 'g_HLJ', 'g_HEN', 'g_HUB', 'g_HUN', 'g_JS', 'g_JX', 'g_JL', 'g_LN', 'g_NMG', 'g_NX', 'g_QH', 'g_SD', 'g_SH', 'g_SX', 'g_SAX', 'g_SC', 'g_TJ', 'g_XJ', 'g_XZ', 'g_YN', 'g_ZJ', 'g_CN']
    #areaArr = ['g_HAIN', 'g_HB', 'g_HLJ', 'g_HEN', 'g_HUB', 'g_HUN', 'g_JS', 'g_JX', 'g_JL', 'g_LN', 'g_NMG', 'g_NX', 'g_QH', 'g_SD', 'g_SH', 'g_SX', 'g_SAX', 'g_SC', 'g_TJ', 'g_XJ', 'g_XZ', 'g_YN', 'g_ZJ', 'g_CN']
    #areaArr = ['g_HB', 'g_HLJ', 'g_HEN', 'g_HUB', 'g_HUN', 'g_JS', 'g_JX', 'g_JL', 'g_LN', 'g_NMG', 'g_NX', 'g_QH', 'g_SD', 'g_SH', 'g_SX', 'g_SAX', 'g_SC', 'g_TJ', 'g_XJ', 'g_XZ', 'g_YN', 'g_ZJ', 'g_CN']
    #areaArr = ['g_HEN', 'g_HUB', 'g_HUN', 'g_JS', 'g_JX', 'g_JL', 'g_LN', 'g_NMG', 'g_NX', 'g_QH', 'g_SD', 'g_SH', 'g_SX', 'g_SAX', 'g_SC', 'g_TJ', 'g_XJ', 'g_XZ', 'g_YN', 'g_ZJ', 'g_CN']
    #areaArr = ['g_HUN', 'g_JS', 'g_JX', 'g_JL', 'g_LN', 'g_NMG', 'g_NX', 'g_QH', 'g_SD', 'g_SH', 'g_SX', 'g_SAX', 'g_SC', 'g_TJ', 'g_XJ', 'g_XZ', 'g_YN', 'g_ZJ', 'g_CN']
    #areaArr = ['g_NX', 'g_QH', 'g_SD', 'g_SH', 'g_SX', 'g_SAX', 'g_SC', 'g_TJ', 'g_XJ', 'g_XZ', 'g_YN', 'g_ZJ', 'g_CN']
    #areaArr = ['g_QH', 'g_SD', 'g_SH', 'g_SX', 'g_SAX', 'g_SC', 'g_TJ', 'g_XJ', 'g_XZ', 'g_YN', 'g_ZJ', 'g_CN']
    #areaArr = ['g_YN', 'g_ZJ', 'g_CN']

    for area in areaArr:
        startPage = 1
        #if area == 'g_HLJ':
            #startPage = 5
        for num in range(startPage,3):
            print("开始抓取"+area+'第'+str(num)+'页数据')
            url = base_url.format(area=area, pagenum=num)
            req  = requests.get(url,headers=headers)
            # 判断网站是否正常打开
            if req.status_code == 200 :
                soup = BeautifulSoup(req.text,'html.parser')
                data = soup.find_all(class_='panel-default')
                for item in data:
                    # 获取每个页面的地址，然后发送到contentPage中处理
                    conpany_url =head_url+item.find('a',{'class':'list-group-item clearfix'})['href']
                    print ('企查查页面地址:%s' % conpany_url)

                    contentPage(conpany_url)
                        
                    tnum = random.randint(2,8)
                    print ('防止网站禁止爬虫，等待%s秒' % tnum)
                    time.sleep(tnum)
            else:
                sys.exit('网站打开异常，爬虫自动退出.')


if __name__ == '__main__':
    r = redis.Redis(host='47.105.174.154', port=6379,db=0)
    # 获取爬虫开始时间
    start_time = datetime.now()
    print ('获取企查查地区的企业信息')
    print ('爬虫开始')
    # csv文件表格的列表头
    '''with open('qichacha_company.csv','a+',newline='',encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(csv_List_head)'''
    main()
    # 获取爬虫结束时间
    end_time = datetime.now()
    # 获取爬虫花费的时间
    use_time = end_time - start_time
    print ('爬虫结束,耗时%s，数据保存在qichacha_company.csv中' % use_time)