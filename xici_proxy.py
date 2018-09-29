import pymysql
import requests
from lxml import etree


class XiciProxy(object):
    def __init__(self):
        self.url = "http://www.xicidaili.com/nn/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.5702.400 QQBrowser/10.2.1893.400',
        }

        self.proxies = {
            'https': '106.75.226.36:808',
        }
        self.db_name = 'ips_db'
        self.host = 'localhost'
        self.user = 'root'
        self.pwd = '123456'
        self.table_name = 'xici3'

    def getProxyList(self, n):
        for i in range(1, n):
            response = requests.get(self.url + str(i), headers=self.headers, proxies=self.proxies)
            self.parseHtml(response.text)
            print("get proxy success!")

    def parseHtml(self, html):
        selector = etree.HTML(html)
        list = selector.xpath("//tr")
        data = []
        for tr in list[1:]:
            ip = tr.xpath(".//td[2]/text()")[0]
            port = tr.xpath(".//td[3]/text()")[0]
            try:
                site = tr.xpath(".//td[4]/a/text()")[0]
            except Exception as e:
                site = ""
            high = tr.xpath(".//td[5]/text()")[0]
            type = tr.xpath(".//td[6]/text()")[0]
            item = {'ip': ip, 'port': port, 'site': site, 'high': high, 'type': type}
            data.append(item)
        self.writeList2Mysql(data)

    def writeList2Mysql(self, data):
        conn = pymysql.connect(
            self.host,
            self.user,
            self.pwd,
        )
        cursor = conn.cursor()
        sql = 'create database if not exists {}'.format(self.db_name)
        cursor.execute(sql)
        cursor.execute("use {}".format(self.db_name))
        sql = "create table if not exists {} (id INT AUTO_INCREMENT PRIMARY KEY,ip VARCHAR(20),port VARCHAR(10),site VARCHAR(20),high_conceal VARCHAR(10),type VARCHAR(10),available BOOLEAN)".format(
            self.table_name)
        cursor.execute(sql)
        for item in data:
            sql = "select * from {} where ip='{}'".format(self.table_name, item['ip'])
            cursor.execute(sql)
            result = cursor.fetchone()
            if result == None:
                sql = "insert into {} (ip,port,site,high_conceal,type,available) values(%s,%s,%s,%s,%s,%c)".format(
                    self.table_name)
                val = (item['ip'], item['port'], item['site'], item['high'], item['type'], 1)
                print(val)
                cursor.execute(sql, val)
                conn.commit()




if __name__ == "__main__":
    xici = XiciProxy()
    xici.getProxyList(20)
