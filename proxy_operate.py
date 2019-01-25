import threading

import pymysql
import requests
from requests.exceptions import ProxyError,ConnectTimeout


class ProxyOperate(object):
    def __init__(self):
        self.table_name = "train12306"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.5702.400 QQBrowser/10.2.1893.400',
            'Host': r'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',

        }
        self.conn = pymysql.connect(
            'localhost',
            'root',
            '123456',
            'ips_db',
        )
        self.cursor = self.conn.cursor()
        self.threadLock = threading.Lock()
        self.index = 0

    def getRandomIp(self):
        sql = "select * from {} where available=1 order by rand() limit 1".format(self.table_name)
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return result[-2].lower(), result[1], result[2]

    def judge_ip(self, http, ip, port):
        test_url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ'
        proxy_url = '{}://{}:{}'.format(http, ip, port)
        print(proxy_url)
        proxies = {
            http: proxy_url
        }
        try:
            response = requests.get(test_url, headers=self.headers, proxies=proxies, timeout=3)
        except ProxyError:
            print("代理出错")
            return False
        except ConnectTimeout:
            print("连接超时")
            return False
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
            self.disable_ip(ip)
            # self.delete_ip(ip)

    def checkAllProxy(self):
        sql = "select * from {} where available=1".format(self.table_name)
        self.cursor.execute(sql)
        self.results = self.cursor.fetchall()
        self.index = 0
        threads = [threading.Thread(target=self.run) for i in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def disable_ip(self, ip):
        sql = "update {} set available={} where ip='{}'".format(self.table_name, 0, ip)
        self.cursor.execute(sql)
        self.conn.commit()
        print(self.cursor.rowcount, " 条记录标记无效")

    def delete_ip(self, ip):
        sql = "delete from {} where ip='{}'".format(self.table_name, ip)
        self.cursor.execute(sql)
        self.conn.commit()
        print(self.cursor.rowcount, " 条记录删除成功")

    def run(self):
        while self.index < len(self.results):
            result = self.results[self.index]
            self.index = self.index + 1
            print(result)
            available = self.judge_ip(result[-2].lower(), result[1], result[2])
            if not available:
                self.threadLock.acquire()
                self.disable_ip(result[1])
                self.threadLock.release()


if __name__ == '__main__':
    print("开始处理")
    operate = ProxyOperate()
    operate.checkAllProxy()
    # operate.checkRandomProxy()
    print("处理结束")
