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
        self.table_name = 'xici'

    def getProxyList(self, n):
        for i in range(1, n):
            response = requests.get(self.url + str(i), headers=self.headers,proxies=self.proxies)
            self.parseHtml(response.text)
            print("get proxy success!")

    def parseHtml(self, html):
        selector = etree.HTML(html)

        iplist = selector.xpath('//tr/td[2]')
        portlist = selector.xpath('//tr/td[3]')
        sitelist = selector.xpath('//tr/td[4]')
        highlist = selector.xpath('//tr/td[5]')
        typelist = selector.xpath('//tr/td[6]')
        self.write2mysql(iplist, portlist, sitelist, highlist, typelist)

    def write2mysql(self, iplist, portlist, sitelist, highlist, typelist):
        conn = pymysql.connect(
            self.host,
            self.user,
            self.pwd,
        )
        cursor = conn.cursor()
        sql = 'create database if not exists {}'.format(self.db_name)
        cursor.execute(sql)
        cursor.execute("use {}".format(self.db_name))
        sql = "create table if not exists {} (id INT AUTO_INCREMENT PRIMARY KEY,ip VARCHAR(20),port VARCHAR(10),site VARCHAR(20),high_conceal VARCHAR(10),type VARCHAR(10))".format(
            self.table_name)
        cursor.execute(sql)
        for ip, port, site, high, type in zip(iplist, portlist, sitelist, highlist, typelist):
            if ip.text and port.text and site.text and high.text and type.text:
                sql = "insert into {} (ip,port,site,high_conceal,type) values(%s,%s,%s,%s,%s)".format(self.table_name)
                val = (ip.text, port.text, site.text, high.text, type.text)
                print(val)
                cursor.execute(sql, val)
                conn.commit()


if __name__ == "__main__":
    xici = XiciProxy()
    xici.getProxyList(10)
