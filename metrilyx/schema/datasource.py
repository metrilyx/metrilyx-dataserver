
import logging
import pandas
import numpy

from twisted.internet import defer

from provider.httpprovider import HttpProvider
from provider.opentsdb import OpenTSDBProvider

import aliasing
import serializer

from uuids import UUID

from pprint import pprint

logger = logging.getLogger(__name__)

SUPPORTED_PROVIDERS = {
    "http": HttpProvider,
    "opentsdb": OpenTSDBProvider
}

class Datasource(serializer.ISerializer):

    def __init__(self, **kwargs):
        
        if kwargs.has_key("id"):
            self.id = kwargs["id"]
        else:
            self.id = str(UUID())

        try:
            self.type =  kwargs["type"]
        except:
            raise RuntimeError("Datasource type not provided!")
        
        if kwargs.has_key("alias") and kwargs["alias"] != None:
            self.alias = kwargs["alias"]
        else:
            self.alias = ""

        if kwargs.has_key("transform"):
            self.transform = kwargs["transform"]
        else:
            self.transform = ""

        try:
            self.provider = SUPPORTED_PROVIDERS[self.type](**kwargs["provider"])
        except Exception, e:
            print "ERROR", e, kwargs
            raise RuntimeError("Invalid provider: %s" % (e))

        # transformed data from provider
        self.data = None

        # Holds fetcher client (e.g. http, https...)
        self.__fetcher = None
        # deferred for after transform
        self.__ddfd = defer.Deferred()


    def __onProviderResponse(self, prov, *args):
        logger.debug("%s %s %s" % (type(prov), prov, args))
        
        df = None
        if type(prov) == OpenTSDBProvider:
            # Do i need to keep df ???
            df = prov.data.DataFrame(convertTime=True)

        else:
            df = prov.data

        self.data = self.applyTransform(df)
        # TODO: set MultiIndex based on unique tags.
        self.__ddfd.callback(self)


    def __onProviderError(self, error, *args):
        # enrich
        if type(error.value) == defer.CancelledError:
            return
            
        self.data = error.value.data
        logger.error("%s %s" % (self.data, args))
        self.__ddfd.errback(self)


    def fetch(self, **kwargs):
        self.__fetcher = self.provider.fetch(**kwargs)        
        self.__fetcher.addCallbacks(self.__onProviderResponse, self.__onProviderError)
        return self.__ddfd

    def cancelRequest(self):
        if self.__fetcher != None:
            self.__fetcher.cancel()

        self.__ddfd.cancel()


    def getTransformIds(self, metas):
        # Parse strings to dict
        mObjs = [ aliasing.DataAlias('', mstr).parseMetadata() for mstr in metas ]
        # Get intersection dict and convert to string
        iMetaStr = aliasing.getMetaString(dict(set.intersection(*(set(m.iteritems()) 
                                                                    for m in mObjs))))
        # Get lambda function body
        lFunc = aliasing.getLambdaContent(self.transform)
        # Prepend lambda func to intersection string
        suffix = lFunc+":"+iMetaStr
        # Prepend index to create unique id.
        return [ str(i)+":"+suffix for i in range(len(metas)-1) ]


    def applyTransform(self, df):
        """
            Applies the transfrom to a given dataframe, i.e. perform operations
            
            Params:
                df : pandas.DataFrame to transform
            Returns:
                Transformed pandas.DataFrame
        """
    
        if self.transform != "":
            try:
                tdf = eval(self.transform)(df)
                # Convert to dataframe if transform results in a Series
                if isinstance(tdf, pandas.Series):
                    # Calculate id as the transform may not have one.
                    tids = self.getTransformIds(df.columns.values)
                    tdf = pandas.DataFrame({tids[0]: tdf})
                return tdf
            
            except Exception,e:
                logger.debug("Could not apply transform: "+self.transform+", err: " + str(e))
        
        return df

    def aggr(self):
        """
        Needed for serializer
        """
        return self.provider.aggr()

