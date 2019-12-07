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

# ��ҵ�б�
base_url = 'https://s.hc360.com/company/search.html?kwd=&z={area}&pnum={page}'
# ����ͷ
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
    'Connection': 'close',
}

# csv���б�ͷ
csv_List_head=('��ҵ����','��ϵ��','��ϵ�绰','��ϵ�ֻ�','��ַ','����')

def getAllCategory():
    provList = [{'name': '����', 'province': ['����', '���', '�ӱ�ʡ', 'ɽ��ʡ', '���ɹ�������'], 'city': [[], [], ['ʯ��ׯ��', '������', '������', '�ȷ���', '��ɽ��', '��̨��', '������', '��ˮ��', '�ػʵ���', '�żҿ���', '�е���'], ['̫ԭ��', '�˳���', '�ٷ���', '��ͬ��', '������', '������', '������', '��Ȫ��', '������', '˷����', '������'], ['���ͺ�����', '��ͷ��', '�����', '���ױ�����', 'ͨ����', '������˹��', '�����׶�����', '���ֹ�����', '�����첼��', '�˰���', '�ں���', '����������']]}, {'name': '����', 'province': ['����ʡ', '����ʡ', '������ʡ'], 'city': [['������', '������', '��ɽ��', '������', 'Ӫ����', '������', '��˳��', '������', '��«����', '������', '������', '�̽���', '������', '��Ϫ��'], ['������', '������', '�ӱ߳�����������', 'ͨ����', '��ƽ��', '�׳���', '��ԭ��', '��ɽ��', '��Դ��'], ['��������', '������', '���������', '��ľ˹��', '������', 'ĵ������', '������', '�ں���', '�绯��', '˫Ѽɽ��', '�׸���', '��̨����', '���˰������']]}, {'name': '����', 'province': ['�Ϻ�', '����ʡ', '�㽭ʡ', '����ʡ', '����ʡ', '����ʡ', 'ɽ��ʡ'], 'city': [[], ['������', '�Ͼ���', '������', '������', '������', '��ͨ��', '������', '̩����', '�γ���', '����', '���Ƹ���', '������', '��Ǩ��'], ['������', '������', '������', '����', '̨����', '������', '������', '������', '��ˮ��', '������', '��ɽ��'], ['�Ϸ���', '������', '������', '�ߺ���', '������', '������', '������', '��ɽ��', '������', '������', '������', '������', '������', '��ɽ��', '������', 'ͭ����', '������'], ['������', 'Ȫ����', '������', '������', '������', '������', '������', '������', '��ƽ��'], ['�ϲ���', '������', '������', '�Ž���', '������', '������', '��������', 'Ƽ����', '������', '�˴���', 'ӥ̶��'], ['������', '�ൺ��', '�Ͳ���', '��ׯ��', '��Ӫ��', '��̨��', '������', 'Ϋ����', '������', '̩����', '������', '������', '������', '������', '�ĳ���', '������', '������', '������']]}, {'name': '����', 'province': ['����ʡ', '����ʡ', '����ʡ', '�㶫ʡ', '����ʡ', '����ʡ'], 'city': [['֣����', '������', '������', '������', '������', '������', '�����', '������', 'ƽ��ɽ��', '�ܿ���', '������', '�����', '������', 'פ�����', '�ױ���', '����Ͽ��', '�����', '��Դ��'], ['�人��', '�差��', '�˲���', '������', 'ʮ����', 'Т����', '�Ƹ���', '��ʩ����������������', '��ʯ��', '������', '������', '������', '������', 'Ǳ����', '��ũ��������', '������', '������'], ['��ɳ��', '��̶��', '������', '������', '������', '������', '������', '������', '������', '������', '¦����', '������', '��������������������', '�żҽ���'], ['������', '������', '��ݸ��', '��ɽ��', '��ɽ��', '������', '�麣��', '��ͷ��', '������', '������', '������', '÷����', 'ï����', '������', '��Զ��', '�ع���', 'տ����', '��Դ��', '��β��', '�Ƹ���', '������'], ['������', '������', '������', '������', '�����', '��ɫ��', '������', '������', '������', '�ӳ���', '���Ǹ���', '������', '������', '������'], ['������', '������', '��ɳ����������', '�Ͳ�����', '��ָɽ��', '�Ĳ���', '������', '������', '������', '����', '������', '��ͤ��������������', '��������������', '������������������', '�ٸ���', '�ֶ�����������', '��ˮ����������', '����']]}, {'name': '����', 'province': ['����', '�Ĵ�ʡ', '����ʡ', '����ʡ', '����������'], 'city': [[], ['�ɶ���', '������', '������', '�ϳ���', '�˱���', '��ɽ��', '������', '������', '�Թ���', '��Ԫ��', '��ɽ����������', '�㰲��', '�ڽ���', '��֦����', '������', 'üɽ��', '������', '������', '�Ű���', '���Ӳ���Ǽ��������', '���β���������'], ['������', '������', 'ǭ�������嶱��������', 'ǭ���ϲ���������������', '�Ͻڵ���', '����ˮ��', 'ͭ�ʵ���', 'ǭ�ϲ���������������', '��˳��'], ['������', '��ɽ׳������������', '��ɽ��', '������', '��Ϫ��', '�������������', '��˫���ɴ���������', '��ͨ��', '��������������', '������', '�º���徰����������', '�������������', '��ӹ���������������', '�ٲ���', 'ŭ��������������', '�ն���'], ['������', '������', '������', '������', '��֥��', '�տ�����', 'ɽ����']]}, {'name': '����', 'province': ['����ʡ', '����ʡ', '�ຣʡ', '���Ļ���������', '�½�ά���������'], 'city': [['������', '������', '������', '������', '������', 'μ����', '�Ӱ���', '������', '������', 'ͭ����'], ['������', '������', '��ˮ��', '��Ȫ��', '������', 'ƽ����', '��Ҵ��', '������', '¤����', '������', '���Ļ���������', '�����', '��������', '���ϲ���������'], ['������', '��������������', '�������������', '���ϲ�����������', '������', '�����ɹ������������', '��������������', '���ϲ���������'], ['������', 'ʯ��ɽ��', '������', '��ԭ��', '������'], ['��³ľ����', '��ʲ����', '���������ɹ�������', '���������������', '�����յ���', '������', '���ܵ���', '�������', '��³������', '��������', '���������ɹ�������', '��������������', '����������', '�������տ¶�����������', 'ʯ������', 'ͼľ�����', '�������']]}]

    areaArr = []
    for prov in provList:
       for i in range(0, len(prov['city'])):
            area = "�й�:" + prov['province'][i]
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
    print('��ֹ��վ��ֹ���棬�ȴ�%s��' % tnum)
    time.sleep(tnum)'''
    print(detailUrl)
    '''tnum = random.randint(2, 5)
    print('��ֹ��վ��ֹ���棬�ȴ�%s��' % tnum)
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
        if infoItem.text == '��ϵ��':
            people = rightArr[i].find('span').find('a').text.strip()
        if infoItem.text == '�绰':
            phone = rightArr[i].text.strip()
        if infoItem.text == '�ֻ�':
            mobile = rightArr[i].text.strip()
        if infoItem.text == '����':
            web = rightArr[i].find('a').text.strip()
        if infoItem.text == '��ַ':
            address = rightArr[i].text.strip()

    if "**" in phone:
        try:
            leftArr = soup.find('div', {'class': 'ContactBox'}).find('ul').findAll('li')
        except Exception:
            return
        for left in leftArr:
            infoItem = left.findAll('span')
            if infoItem[0].text == '�绰':
                phone = infoItem[1].text.strip("��")
    if "**" in mobile:
        try:
            leftArr = soup.find('div', {'class': 'ContactBox'}).find('ul').findAll('li')
        except Exception:
            return
        for left in leftArr:
            infoItem = left.findAll('span')
            if infoItem[0].text == '�ֻ�':
                mobile = infoItem[1].text.strip("��")

    conpany_msg = (shopName, people, phone, mobile, web, address)
    had = r.get(mobile+' '+phone)
    if (phone or mobile) and (had is None):
        r.set(mobile+' '+phone, shopName)
        print('��ҵ����: %s' % shopName)
        print('��ϵ��: %s' % people)
        print('��ϵ�绰: %s' % phone)
        print('��ϵ�ֻ�: %s' % mobile)
        print('��ַ: %s' % address)
        print('����: %s' % web)
        save_csv(conpany_msg)
    else:
        print('�ֻ���'+mobile+' '+phone)

#�������ݵ�csv�ļ�
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
        print("��"+str(page)+"ҳ")
        url = base_url.format(area=area, page=page)
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.text, "html.parser")
        contactLinkList = soup.find_all('dt', {'class': 'til'})
        for contactLink in contactLinkList:
            detailUrl = contactLink.find('h3').find('a').get('href')
            detailUrl = detailUrl + 'shop/company.html'
            shopName = contactLink.find('h3').find('a').text.strip()
            getDetailInfo(detailUrl, shopName)


# ������
def main():
    areaList = getAllCategory()  #362
    #getCompanyList(areaList[0])
    cate = open('cate.txt', 'r').read() if os.path.isfile('cate.txt') else '55'
    for i in range(int(cate), len(areaList)):
        if int(cate) != i:
            open('page.txt', 'wb').write(str(1).encode('utf-8'))
        open('cate.txt', 'wb').write(str(i).encode('utf-8'))
        print("��"+str(i)+"������")
        getCompanyList(areaList[i], i)
        #thread = threading.Thread(target=getCompanyList,args=(areaList[i], i,))
        #thread.start()


if __name__ == '__main__':
    r = redis.Redis(host='47.105.174.154', port=6379,db=0)
    # ��ȡ���濪ʼʱ��
    start_time = datetime.now()
    print ('��ȡ�۴�������ҵ��Ϣ')
    print ('���濪ʼ')
    # csv�ļ������б�ͷ
    with open('huichong.csv','a+',newline='',encoding='utf-8-sig') as datacsv:
        csvwriter = csv.writer(datacsv,dialect=('excel'))
        csvwriter.writerow(csv_List_head)
    main()
    # ��ȡ�������ʱ��
    end_time = datetime.now()
    # ��ȡ���滨�ѵ�ʱ��
    use_time = end_time - start_time
    print ('�������,��ʱ%s�����ݱ�����huichong.csv��' % use_time)