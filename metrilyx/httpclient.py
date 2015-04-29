

import StringIO
import gzip

import ujson as json

from twisted.python.log import err
from twisted.web.client import Agent
from twisted.web.iweb import IBodyProducer
from twisted.web.http_headers import Headers
from twisted.internet import reactor, defer
from twisted.internet.ssl import ClientContextFactory
from twisted.internet.protocol import Protocol

from zope.interface import implements

DEFAULT_REQ_HEADERS = {
    "Accept-Encoding": ["gzip"],
    "User-Agent": ["AsyncHttpClient"]
    }


class BodyProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        if isinstance(body, str):
            self.body = body
        else:
            json.dumps(body)

        self.length = len(self.body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


class WebClientContextFactory(ClientContextFactory):
    ''' For SSL support '''
    def getContext(self, hostname, port):
        return ClientContextFactory.getContext(self)


class AsyncHttpResponseProtocol(Protocol):
    def __init__(self, finished_deferred, response):
        self.__httpResp = response
        #self.headers = headers
        self.finished = finished_deferred
        self._data = ""

    def dataReceived(self, bytesRecvd):
        self._data += bytesRecvd

    def __ungzip_(self):
        try:
            compressedstream = StringIO.StringIO(self._data)
            gzipper = gzip.GzipFile(fileobj=compressedstream)
            return gzipper.read()
        except Exception,e:
            #return json.dumps({"error": str(e)})
            self.finished.errback([e, self.__httpResp])

    def connectionLost(self, reason):
        #print "REASON", reason.value.reasons[1]
        if self.__httpResp.headers.hasHeader('content-encoding') and \
                ('gzip' in self.__httpResp.headers.getRawHeaders('content-encoding')):
            
            d = self.__ungzip_()
            #logger.debug("Gzipped data: %s" % (d))
            self.finished.callback([d, self.__httpResp])
        else:
            self.finished.callback([self._data, self.__httpResp])


class HttpClient(object):
    
    def __init__(self, *args, **kwargs):

        contextFactory = WebClientContextFactory()
        agent = Agent(reactor, contextFactory)

        body = None
        if kwargs.has_key("body") and kwargs["body"] != None:
            body = BodyProducer(kwargs["body"])

        headers = DEFAULT_REQ_HEADERS
        if kwargs.has_key("headers"):
            headers.update(kwargs["headers"])

        self.response = defer.Deferred()
        self.__agentDeferred = agent.request(
            str(kwargs["method"]), 
            str(kwargs["url"]), 
            Headers(headers), body)

        self.__agentDeferred.addCallbacks(self.__httpRespCb, self.__httpRespEb)

    def __httpRespCb(self, response, *args):
        response.deliverBody(AsyncHttpResponseProtocol(self.response, response))

    def __httpRespEb(self, error, *args):
        self.response.errback(error)

    def cancelRequest(self):
        self.response.cancel()
        self.__agentDeferred.cancel()
        