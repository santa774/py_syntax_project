# -*-coding:utf-8-*-
import socket
import re
import sys
from multiprocessing import Process

STATIC_PAGE_ROOT_LOCATION = "./html"
DYNAMIC_PAGE_ROOT_LOCATION = "./wsgipython"


class HttpServer():
    """
    web服务器
    """
    def __init__(self):
        self.serSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 复用socket
        self.serSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def bind_addr(self, addr):
        self.serSocket.bind(addr)

    def start(self):
        self.serSocket.listen(10)
        while True:
            clientSocket, newAddr = self.serSocket.accept()
            print("%s , %s连接上了" % (newAddr))
            clientProcess = Process(target=self.handleClient, args=(clientSocket,))
            clientProcess.start()
            clientSocket.close()

    def start_response(self, status, headers):
        self.response_headline = "HTTP/1.1 %s\r\n" % status
        for header in headers:
            self.response_headline += "%s: %s\r\n" % header
        self.response_headline += "\r\n"

    # 处理客户端请求
    def handleClient(self, clientSocket):
        # 接受客户发送的请求
        requestData = clientSocket.recv(1024)
        print("收到的数据:%s" % (requestData))
        # 拆分获取请求中的具体请求页面，使用正则表达式提取出需要的数据
        requestDataList = requestData.splitlines()
        requestHeader = requestDataList[0]  # excample: GET / HTTP/1.1
        print(requestHeader.decode("utf-8"))
        requestPageName = re.match(r"\w+ +(/[^ ]*) ", requestHeader.decode("utf-8")).group(1)

        # 包括所有Http请求头
        environ = {}

        # 判断客户端请求的是动态还是静态
        if requestPageName.endswith(".py"):
            # 获取需要执行的动态程序名   /ctime.py -> ctime
            exeName = __import__(requestPageName[1:-3])
            responseBody = exeName.application(environ, self.start_response)
            response = self.response_headline + responseBody
        else:
            if "/" == requestPageName:
                requestPageName = "/index.html"

            try:
                print(requestPageName)
                file = open(STATIC_PAGE_ROOT_LOCATION + requestPageName, "rb")
            except:
                responseHeaderLines = "HTTP/1.1 404 Not Found\r\n"
                responseHeaderLines += "Server: my server\r\n"
                responseHeaderLines += "\r\n"
                responseBody = "The page is not find"
            else:
                pageData = file.read()
                file.close()
                responseHeaderLines = "HTTP/1.1 200 OK\r\n"
                responseHeaderLines += "Server: my server\r\n"
                responseHeaderLines += "\r\n"
                responseBody = pageData.decode("utf-8")
            response = responseHeaderLines + responseBody
        clientSocket.send(bytes(response, "utf-8"))
        clientSocket.close()


def main():
    sys.path.insert(1, DYNAMIC_PAGE_ROOT_LOCATION)
    serSocket = HttpServer()
    serSocket.bind_addr(("", 8000))
    serSocket.start()


if __name__ == "__main__":
    main()
