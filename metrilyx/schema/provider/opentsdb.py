
import ujson as json

from httpprovider import HttpProvider

from opentsdb_pandas.response import OpenTSDBResponse

from ...httpclient import HttpClient

import logging

from pprint import pprint

logger = logging.getLogger(__name__)


class OpenTSDBQuery(object):
    def __init__(self, *args, **kwargs):
        if kwargs.has_key("msResolution"):
            self.msResolution = msResolution
        else:
            self.msResolution = True

        self.metric = kwargs["metric"]

        if kwargs.has_key("aggregator"):
            self.aggregator = kwargs["aggregator"]
        else:
            self.aggregator = "sum"

        if kwargs.has_key("rate"):
            self.rate = kwargs["rate"]
        else:
            self.rate = False

        if kwargs.has_key("tags"):
            self.tags = kwargs["tags"]
        else:
            self.tags = {}

        if kwargs.has_key("rateOptions"):
            self.rateOptions = kwargs["rateOptions"]
            #counter bool
            #counterMax
            #resetValue
        
        if kwargs.has_key("downsample"):
            self.downsample = kwargs["downsample"]

    def uniqueTagKeys(self):
        out = []
        for k,v in self.tags.items():
            if "*" in v or "|" in v:
                out.append(k)

        return out



class OpenTSDBProvider(HttpProvider):
    """
    OpenTSDBProvider

    """
    def __init__(self, **kwargs):
        super(OpenTSDBProvider, self).__init__(**kwargs)
        
        del self.body
        del self.normalizer

        self.query = OpenTSDBQuery(**kwargs["query"])

    def aggr(self):
        """ Return the aggregator """
        return self.query.aggregator

    def __responseCallback(self, response, *args):
        logger.debug("Partial result (opentsdb): %s %s" % (response[1].code, args))
        if response[1].code >= 400:
            #print response.text()
            #treq.json_content(response).addCallback(self.__assignData)
            logger.error(response[0])
            jd = json.loads(response[0])
            self.data = { 'error': jd['error']['message'] }
            self._pdfd.errback(self)
            return
        
        # TODO: convert to dataframe
        self.data = OpenTSDBResponse(response[0])
        
        self._pdfd.callback(self)


    def __responseErrback(self, error, *args):
        logger.error("opentsdb %s %s" % (error.value.message, args))
        #pprint(dir(error.value))
        self.data = { "error": error.value.message }
        #self.data = error.value.json()

        self._pdfd.errback(self)


    def __queryParams(self, **kwargs):
        """
            @param: kwargs global args from panel
            @type dict 
        """
        #if not kwargs.has_key("start"):
        #    self._client.response.errback("OpenTSDB 'start' key required!")
        #prefix = ""
        prefix = "start=%s&" % (kwargs["start"])

        if kwargs.has_key("end"):
            prefix += "end=%s&" % (kwargs["end"])

        if self.query.rate:
            prefix += "m=%s:rate:%s" % (self.query.aggregator, self.query.metric)
        else:
            prefix += "m=%s:%s" % (self.query.aggregator, self.query.metric)

        tags = ",".join(["%s=%s" % (k,v) for k,v in self.query.tags.items()])
        
        if tags == "":
            return prefix
        else:
            return "%s{%s}" % (prefix, tags)

    def fetch(self, **kwargs):
        url = self.url + "?" + self.__queryParams(**kwargs)
        logger.debug("Fetching (opentsdb): %s %s" % (self.method, url))

        self._client = HttpClient(url=url, method=self.method)
        self._client.response.addCallbacks(self.__responseCallback, self.__responseErrback)

        return self._pdfd


    def __parseId(self, _id):
        """ Parse column id for metadata used to normalize the alias """
        if "{" in _id:
            (metric, tags) = _id.split("{")
            tags = tags[:-1]
            
            meta = { "metric": metric }
            for tkv in tags.split(","):
                (tk, tv) = tkv.split("=")
                meta['tags.'+tk] = tv
            return meta
        else:
            return { "metric": _id }


    def normalizedAlias(self, metaStr, aliasStr):
        """
            metaStr: dataframe column id containing the full tsdb metric name
            aliasStr : alias to apply
        """
        
        logger.debug("!!!!!++++> "+metaStr)
        meta = self.__parseId(metaStr)
        
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
            utags = self.query.uniqueTagKeys()
            if len(utags) > 0:
                tagstr = ",".join([ "%s=%s" % (ky, meta["tags."+ky]) for ky in utags ])
                nAlias = "%s{%s}" % (self.query.metric, tagstr)    
            else:
                nAlias = metaStr

        return nAlias