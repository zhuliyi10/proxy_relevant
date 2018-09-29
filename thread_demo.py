import threading
import time


threadLock=threading.Lock()
class MyThread(threading.Thread):
    def run(self):
        for i in range(5):
            threadLock.acquire()
            print("thread:{},num:{}".format(self.name, i))
            time.sleep(1)
            threadLock.release()


if __name__ == '__main__':
    print("start main")
    threads = [MyThread() for i in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print("end main")
