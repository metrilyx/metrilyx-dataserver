
import ujson as json
from twisted.internet import defer
import pandas

from interface import IProvider

from ...httpclient import HttpClient
from .. import aliasing

import logging

logger = logging.getLogger(__name__)


class HttpProvider(IProvider):

    def __init__(self, **kwargs):
        self.url = kwargs['url']
        self.method = kwargs['method']
        
        if kwargs.has_key('name'):
            self.name = kwargs['name']

        if kwargs.has_key('params'):
            self.params = kwargs['params']

        if kwargs.has_key("normalizer"):
            self.normalizer = kwargs["normalizer"]
        else:
            self.normalizer = ""
        
        if kwargs.has_key('body'):
            self.body = kwargs['body']
        else:
            self.body = None
        
        if kwargs.has_key('aggregator'):
            self.aggregator = kwargs['aggregator']
        
        # http client
        self._client = None
        # dfd used by user
        self._pdfd = defer.Deferred()

        # response data
        self.data = None

    def normalizedAlias(self, metaStr, aliasStr):
        ''' THIS DOES NOT WORK.  NEEDS FIXING '''
        '''
        nAlias = metaStr
        if aliasStr.startswith("lambda"):
            try:
                nAlias = eval(aliasStr)(meta)
            except Exception, e:
                logger.warn("Failed to apply alias (lambda): "+aliasStr)
        
        elif aliasStr.startswith("!lambda"):
            try:
                nAlias = eval(aliasStr[1:])(meta)
            except Exception, e:
                logger.warn("Failed to apply alias (lambda): "+aliasStr[1:])

        else:
            try:
                nAlias = aliasStr % (meta)
            except Exception, e:
                logger.warn("Failed to apply alias (string formatted): "+aliasStr)
        
        if nAlias == "":
            nAlias = metaStr

        return nAlias
        '''
        nAlias = aliasing.DataAlias(aliasStr, metaStr).alias()
        if nAlias == "":
            return metaStr

        return nAlias


    def aggr(self):
        """ Return the aggregator """
        return self.aggregator

    def applyNormalizer(self, data):
        if self.normalizer != "":
            logger.debug("Applying normalizer: '"+self.normalizer+"'")
            try:
                #logger.debug(data);
                #logger.debug("Normalizer data: %s" % (type(data)))
                return eval(self.normalizer)(data)
                # TODO: return datastructure with normalized data
                # convertable to DataFrame.
            except Exception, e:
                logger.error("Failed to apply normalizer: %s" % (e))
        return data


    def __responseCallback(self, response, *args, **kwargs):
        #logger.debug("Provider result: %s %s %s" % (response, args, kwargs))
        logger.debug("HTTP provider result: %s" % (type(response[0])))


        if response[1].code >= 400:
            self.data = response[0]
            self._pdfd.errback(self)
            return
        
        # get content type - if not json treat as string.
        if response[1].headers.hasHeader("content-type") and \
                ('json' in response[1].headers.getRawHeaders("content-type")[0]):
        
            self.data = self.applyNormalizer(json.loads(response[0]))
        else:
            self.data = self.applyNormalizer(response[0])
        
        #logger.debug("Provider result: %s" % (self.data))
        
        self._pdfd.callback(self)

    def __responseErrback(self, error, *args):
        
        logger.error("%s %s" %(error.value, args))
        #self.data = { "error": error }
        #self.data = { "error": error.value.text }
        self._pdfd.errback(self)


    def fetch(self, **kwargs):
        url =  self.url
        
        if self.__dict__.has_key("params"):
            url += "?"+ "&".join([ "%s=%s" % (k, v) for k,v in self.params.items() ])

        self._client = HttpClient(url=url, method=self.method, body=self.body)
        self._client.response.addCallbacks(self.__responseCallback, self.__responseErrback)

        return self._pdfd

    
    def cancel(self):
        if self._client != None:
            self._client.cancelRequest()