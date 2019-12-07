from meituan_pc import Meituan
from tool.create_city_list.gitcity import MeituanCity
import csv
import time
import threading



class MeituanSpider(object):
    def __init__(self):
        self.meituan = Meituan()
        self.citylist = MeituanCity._get_city_list()
        self.citylist = self.citylist[1178:]
        self.datalist = []
        self.num = 1
    def savetomongodb(self):
        pass

    def run(self):
        #print(self.citylist)
        #exit()
        '''csv_List_head=('商家名称','商家电话','商家地址','平均消费','开业时间','评分')
        with open('meituan_company.csv','a+',newline='',encoding='utf-8-sig') as datacsv:
            csvwriter = csv.writer(datacsv,dialect=('excel'))
            csvwriter.writerow(csv_List_head)'''
        '''for i in range(0, len(self.citylist)):
            t =threading.Thread(target=self.getCityShop,args=(i,))
            t.start() '''
        while True:
            print("开始抓取第{}个城市的商家信息,城市名称：{}".format(self.num,self.meituan.payload["cityName"]))
            data_dict = {}
            data_lists = []

            while True:
                # 抓取一页的数据
                data = self.meituan.run()
                if not data == []:
                    data_lists.append(data)
                    # 翻页抓取
                    self.meituan.payload["page"] += 1
                else:

                    data_dict[self.meituan.payload["cityName"]] = data_lists
                    self.datalist.append(data_dict)
                    self.meituan.payload["page"] = 1
                    break

            if not self.citylist == []:
                # 切换城市
                self.meituan.payload["cityName"] = self.citylist.pop(0)
                self.num+=1
                print(self.datalist)


            else:
                print("抓取完毕")
                print("统计：本次共抓取城市数量为：{}".format(self.num))
                break
    def getCityShop(self, i):
        '''print("开始抓取第{}个城市的商家信息,城市名称：{}".format(i+1,self.citylist[i]))
        time.sleep(3)
        data_dict = {}
        data_lists = []

        while True:
            # 抓取一页的数据
            data = self.meituan.run()
            if not data == []:
                data_lists.append(data)
                # 翻页抓取
                self.meituan.payload["page"] += 1
            else:

                data_dict[self.meituan.payload["cityName"]] = data_lists
                self.datalist.append(data_dict)
                self.meituan.payload["page"] = 1
                break

        if not self.citylist == []:
            # 切换城市
            self.meituan.payload["cityName"] = self.citylist.pop(0)
            self.num+=1
            print(self.datalist)


        else:
            print("抓取完毕")
            print("统计：本次共抓取城市数量为：{}".format(self.num))
            break'''

a = MeituanSpider()
print(len(a.citylist))
a.run()


