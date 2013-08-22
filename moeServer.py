#coding:utf-8
from twisted.internet import reactor,protocol
import struct,sys


class remoteFacory(protocol.ClientFactory):
    def __init__(self,socks5):
        self.protocol = remoteProtocol
        self.socks5 = socks5

    def clientConnectionFailed(self,connector,reason):
        print 'failed:',reason.getErrorMessage()
        self.socks5.transport.loseConnection()

    def clientConnectionLost(self,connector,reason):
        print 'lost:',reson.getErrorMessage()
        self.socks5.transport.lostConnection()

class remoteProtocol(protocol.Protocol):
    def connectionMade(self):
        self.socks5 = self.factory.socks5
        self.socks5.remote = self.transport
        self.socks5.state = 'connecting'
    # send local the remote data
    def dataReceived(self,data):
        self.socks5.transport.write(data)

    # if remote host lost.Reset the state
    # and close the connection
    def connectionLost(self):
        self.socks5.state = 'listen'
        self.socks5.transport.lostConnection()

class socks5Protocol(protocol.Protocol):
    def connectionMade(self):
        self.state = 'listen'

    def dataReceived(self,data):
        method = getattr(self,self.state)
        method(data)

    def listen(self,data):
        ver,nmethods = struct.unpack('!BB',data[:2])
        if not ver == 5:
            print 'Please use Socket V5?'
            self.tansport.loseConection()
            sys.exit(1)

        if nmethods<1:
            print "What's this!?"
            self.tansport.loseConnection()
            sys.exit(1)

        methods = data[2:2+nmethods]
        for method in methods:
            ## no auth,no need account and pass
            if ord(meth) == 0:
                ## 
                resp = struct.pack('!BB',5,0)
                self.transport.write(resp)
                self.state = 'wait_connect'
                return # continue?
            elif ord(meth) == 2:
                resp = struct.pack('!BB',5,2)
                self.transport.write(resp)
                self.state = 'wait_auth_connect'
                return
            elif ord(meth)==255:
                self.transport.loseConnection()
                return
            else:
                ## maybe use 01,02,03,80....
                ## but it is not necessary
                ## so cut off the connection
                self.transport.loseConnection()

    def wait_connect(self,data):
        ver,cmd,rsv,atyp = struct.unpack('!BBBB',data[:4])
        ## not use the socket v5
        ## or used the rsv...(?)
        if ver != 5 or rsv!=0:
            print "Please use socket v5"
            self.transport.loseConnection()
            return
        data = data[4:]
        ## connect
        if cmd == 1:
            if atyp == 1: #IP V4
                b1,b2,b3,b4 = struct.unpack('!BBBB',data[:4])
                host = '%i.%i.%i.%i' % (b1,b2,b3,b4)
                data = data[4:]
            elif atyp == 3: # domain name
                # the first octet is the number of lenth
                lenth = struct.unpack('!B',data[0])
                lenth = lenth[0]
                host = data[1:1+lenth]
                data = data[1+lenth:]
            elif atyp == 4:#ip v6
                pass
            else:
                self.transport.loseConnection()
                return
            port = struct.unpack('!H',data[:2])
            port = port[0]
            data = data[2:]
            return self.connect(host,port) 
        ## bind
        elif cmd == 2:
            pass
        ## udp associate
        elif cmd == 3:
            pass
        else:
            self.transport.loseConnection()

    def connect(self,host,port):
        facotry = remote_facotry(self)
        reactor.connectTCP(host,port,factory)


def main():
   factory = protocol.ServerFactory() 
   factory.protocol = socks5Protocol
   reactor.listenTCP(11235,factory)
   reactor.run()

if __name__=='__main__':
    main()
