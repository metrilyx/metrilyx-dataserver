
import logging
import pandas
import numpy

from twisted.internet import defer

from provider.httpprovider import HttpProvider
from provider.opentsdb import OpenTSDBProvider

from uuids import UUID

logger = logging.getLogger(__name__)

# non time series graph types.
GRAPH_TYPES_NON_TS = ("bar", "column", "pie")

SUPPORTED_PROVIDERS = {
    "http": HttpProvider,
    "opentsdb": OpenTSDBProvider
}

class Datasource(object):

    def __init__(self, **kwargs):
        
        if kwargs.has_key("id"):
            self.id = kwargs["id"]
        else:
            self.id = str(UUID())

        try:
            self.type =  kwargs["type"]
        except:
            raise RuntimeError("Datasource type not provided!")
        
        if kwargs.has_key("alias"):
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

    
    def __opentsdbColumnDatapoints(self, column):
        """
            Serialize each column to be shipped.
        """
        # drop NaN values
        nonNanSerie = column.replace([numpy.inf, -numpy.inf], numpy.nan).dropna()
        # convert timestamp to milliseconds
        tsIdx = nonNanSerie.index.astype(numpy.int64)/1000000
        # re-combine timestamps and value for the column and return [(...)]
        return zip(tsIdx, nonNanSerie.values)
    

    def __onProviderResponse(self, prov, *args):
        logger.debug("%s %s %s" % (type(prov), prov, args))
        
        df = None
        if type(prov) == OpenTSDBProvider:
            # Do i need to keep df ???
            df = prov.data.DataFrame(convertTime=True)

        else:
            df = prov.data

        self.data = self.applyTransform(df)

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


    def applyTransform(self, df):
        """
            Applies the transfrom to a given dataframe, i.e. perform operations
            
            Params:
                df : pandas.DataFrame to transform
            Returns:
                transformed data.
        """
    
        if self.transform != "":
            try:
                tdf = eval(self.transform)(df)     
                # Convert to dataframe if transform results in a Series
                if isinstance(tdf, pandas.Series):
                    # TODO : FIX naming
                    # check if serie has name
                    tdf = pandas.DataFrame({self.alias: tdf})
                
                return tdf
            
            except Exception,e:
                print "Could not apply transform: ", self.transform, "err:", e
        
        return df


    def panelTypeData(self, panelType):
        """
            All graph types must be of type pandas.DataFrame

            Return:
                list : Serialized data based on the panel type

        """
        if panelType in GRAPH_TYPES_NON_TS:
            out = []

            for col in self.data:
            
                #logger.debug(">>>>> %s" % (col))
                nAlias = self.provider.normalizedAlias(col, self.alias)
                #logger.debug(">>>>> After: %s" % (col))
                cleanCol = self.data[col].replace([numpy.inf, -numpy.inf], numpy.nan).dropna()
                #logger.debug("Aggregator: %s" % (self.provider.aggr()))
                if self.provider.aggr() == "avg":
                    out.append({
                        "id": col,
                        "alias": nAlias,
                        "data": cleanCol.mean()
                    })
                else:
                    out.append({
                        "id": col,
                        "alias": nAlias,
                        "data": eval("cleanCol.%s()" % (self.provider.aggr()))
                    })
            
            return out
        
        elif panelType == "list":
            
            return [{
                "id": "",
                "alias": self.alias,
                "data": it,
            } for it in self.data]

        elif panelType == "text":
            
            return {
                "id":"",
                "alias": self.alias,
                "data": self.data
            }
        else:
            #logger.debug("TSDATA")
            # Time Series data.
            return [{
                "alias": self.provider.normalizedAlias(col, self.alias),
                "id": col,
                "data": self.__opentsdbColumnDatapoints(self.data[col])
                } for col in self.data.columns ]



