
import logging

# non time series graph types.
PANEL_TYPES_NONTS = ("bar", "column", "pie")

logger = logging.getLogger(__name__)


def getLambdaContent(lfunc):
    return ":".join(lfunc.split(":")[1:]).strip()

def getMetaString(metadata):
    tags = ",".join([ "%s=%s" %(k.split(".")[-1], v) for k,v in metadata.items() 
                                                                if k != "metric" ])
    if metadata.has_key("metric"):
        return "%s{%s}" % (metadata["metric"], tags)
    else:
        return "{%s}" %(tags)

class DataAlias(object):
    
    def __init__(self, aliasString, metaString):
        self.aliasString = aliasString
        self.metaString = metaString


    def parseMetadata(self):
        """ 
            Parse meta string (column id) for metadata used to normalize the alias.

        """       
        if self.metaString in (None, ''):
            logger.error("Invalid metadata string: %s %s" %(self.metaString))
            return None

        if "{" in self.metaString:
            (metric, tags) = self.metaString.split("{")
            tags = tags[:-1]
            
            meta = { "metric": metric }
            for tkv in tags.split(","):
                (tk, tv) = tkv.split("=")
                meta['tags.'+tk] = tv
            return meta
        else:
            return { "metric": self.metaString }


    def alias(self):
        """ 
        Return:
            normalized alias 
        """

        logger.debug("Alias alias: '" + self.aliasString + "' metadata: '" + 
            self.metaString + "'")
        meta = self.parseMetadata()
        
        nAlias = self.metaString
        if self.aliasString.startswith("lambda"):
            try:
                nAlias = eval(self.aliasString)(meta)
            except Exception, e:
                logger.warn("Failed to apply alias (lambda): "+self.aliasString)
        
        elif self.aliasString.startswith("!lambda"):
            try:
                nAlias = eval(self.aliasString[1:])(meta)
            except Exception, e:
                logger.warn("Failed to apply alias (lambda): "+self.aliasString[1:])
        elif self.aliasString == "":
            nAlias = self.metaString
        else:
            try:
                nAlias = self.aliasString % (meta)
            except Exception, e:
                logger.warn("Failed to apply alias (string formatted): "+self.aliasString)
        '''
        if nAlias == "":
            utags = self.query.uniqueTagKeys()
            if len(utags) > 0:
                tagstr = ",".join([ "%s=%s" % (ky, meta["tags."+ky]) for ky in utags ])
                nAlias = "%s{%s}" % (self.query.metric, tagstr)    
        '''   
        return nAlias