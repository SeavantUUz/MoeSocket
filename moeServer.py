from twisted.internet import reactor,protocol
import struct


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
        if data:
            self.transport.write('res')
            self.state = 'accept'
        self.transport.lostConnection()

    def accept(self,data):
        (checkPoint,lenth) = struct.unpack('!BB',data[:2])
        # To make sure all things are right
        # maybe I think too much....
        if checkPoint != 0:
            self.transport.loseConnection()

        ## pickle the data
        destFormat = '!{0}sL'.format(lenth)
        ## 2:2+lenth is host and 2+lenth:6+lenth is port
        (host,port) = struct.unpack(hostFormat,data[2:6+lenth])
        return self.remote_connect(host,port)

    def remote_connect(self,host,port):
        factory = remoteFactory(self)
        reactor.connectTCP(host,port,factory)

    def connecting(self,data):
        self.remote.write(data)


    

def main():
   factory = protocol.ServerFactory() 
   factory.protocol = socks5Protocol
   reactor.listen(11235,factory)
   reactor.run()
