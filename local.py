from twisted.internet import reactor,protocol

class remoteFactory(protocol.ClientFactory):
    def __init__(self,local):
        self.local = local
        self.protocol = remoteProtocol

class remoteProtocol(protocol.Protocol):
    def connectionMade(self):
        self.local = self.factory.local
        self.local.remote = self.transport

    def dataReceived(self,data):
        ## transfer the data to local
        self.local.transport.write(data)

class proxyProtocol(protocol.Protocol):
    def __init__(self):
        self.server = 'localhost'
        self.port = 11234
        factory = remoteFactory(self)
        reactor.connectTCP(self.server,self.port ,factory)

    def dataReceived(self,data):
        try:
            self.remote.write(data)
        except AttributeError:
            pass

def main():
    factory = protocol.ServerFactory()
    factory.protocol = proxyProtocol
    reactor.listenTCP(7777,factory)
    reactor.run()

if __name__=='__main__':
    main()
