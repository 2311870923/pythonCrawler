import redis
import csv
import codecs


r = redis.Redis(host='47.105.174.154', port='6379', password='myangel201314', db=0)

with codecs.open(filename='md5_url.csv', mode='a+', encoding='utf-8') as f:
    write = csv.writer(f, dialect='excel')
    for index in range(0, 1200):
        start = index * 10000
        url_list = r.zrange('detail:urls', start, start + 10000)
        for url in url_list:
            write.writerow([url.decode()])
