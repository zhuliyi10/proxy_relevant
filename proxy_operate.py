import pymysql
import requests


class ProxyOperate(object):
    def __init__(self):
        self.table_name = "xici3"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.5702.400 QQBrowser/10.2.1893.400',
        }
        self.conn = pymysql.connect(
            'localhost',
            'root',
            '123456',
            'ips_db',
        )
        self.cursor = self.conn.cursor()

    def getRandomIp(self):
        sql = "select * from {} where available=1 order by rand() limit 1".format(self.table_name)
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        print(result)
        print(result[-2].lower(), result[1], result[2])
        return result[-2].lower(), result[1], result[2]

    def judge_ip(self, http, ip, port):
        test_url = 'https://www.baidu.com/'
        proxy_url = '{}://{}:{}'.format(http, ip, port)
        print(proxy_url)
        proxies = {
            http: proxy_url
        }
        try:
            response = requests.get(test_url, headers=self.headers, proxies=proxies, timeout=2)

        except Exception as e:
            print("代理 {}不可用".format(proxy_url))
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("代理 {}可用".format(proxy_url))
                return True
            else:
                print("代理 {}不可用".format(proxy_url))
                return False

    def checkRandomProxy(self):
        http, ip, port = self.getRandomIp()
        available = self.judge_ip(http, ip, port)
        if not available:
            self.available_ip(ip)
            # self.delete_ip(ip)

    def checkAllProxy(self):
        sql = "select * from {} where available=1".format(self.table_name)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        for result in results:
            print(result)
            available = self.judge_ip(result[-2].lower(), result[1], result[2])
            if not available:
                self.available_ip(result[1])
                # self.delete_ip(result[1])

    def available_ip(self, ip):
        sql = "update {} set available={} where ip='{}'".format(self.table_name, 0, ip)
        self.cursor.execute(sql)
        self.conn.commit()
        print(self.cursor.rowcount, " 条记录标记无效")

    def delete_ip(self, ip):
        sql = "delete from {} where ip='{}'".format(self.table_name, ip)
        self.cursor.execute(sql)
        self.conn.commit()
        print(self.cursor.rowcount, " 条记录删除成功")


if __name__ == '__main__':
    operate = ProxyOperate()
    # operate.checkAllProxy()
    operate.checkRandomProxy()
