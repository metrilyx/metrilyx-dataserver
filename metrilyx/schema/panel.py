
import logging

from twisted.internet import defer

from ..server.response import ResponseData

from datasource import Datasource
from uuids import UUID

from pprint import pprint

logger = logging.getLogger(__name__)

PANEL_ATTRS = ("id", "name", "type", "size", "datasources")


class BasePanel(object):

    def __init__(self, **kwargs):

        if kwargs.has_key("id"):
            self.id = kwargs["id"]
        else:
            self.id = str(UUID())

        self.type = kwargs["type"]

        if kwargs.has_key("name"):
            self.name = kwargs["name"]

        if kwargs.has_key("size"):
            self.size = kwargs["size"]


class Panel(BasePanel):

    def __init__(self, **kwargs):
        super(Panel, self).__init__(**kwargs)
        self.datasources = [ Datasource(**ds) for ds in kwargs["datasources"] ]    

        if kwargs.has_key("secondaries") and kwargs["secondaries"] != None:
            self.secondaries = kwargs["secondaries"]
        else:
            self.secondaries = []


    def applySecondaries(self):
        logger.debug("Checking for secondaries (%s)..." % (self.id))
        
        dss = [ ds.data for ds in self.datasources ]
        # if opentsdb
        for ds in dss:
            # Remove metric name so tags line up when performing the operation. 
            ds.columns = [ "{"+col.split("{")[1] for col in ds.columns.values ]

        for sec in self.secondaries:

            try:
                rslt = eval(self.secondaries[0]['operation'])(*dss)
                print rslt.head()
                # TODO : apply alias.
            except Exception, e:
                logger.error("Secondary operation failed: %s" % (e))
                #return { "error": "Secondary operation failed: %s" % (e) }


class PanelRequest(Panel):

    def __init__(self, **kwargs):
        super(PanelRequest, self).__init__(**kwargs)
        # Xtra global params 
        self._extraArgs = dict([ (k,v) for k, v in kwargs.items() if k not in PANEL_ATTRS ])

        self.__activeSources = 0
        self.__panelRequestDone = None

        # Callback used to send data to client.
        # This gets assigned as part of .fetch()
        self.__sendFunc = None

    def sendResponse(self, data):
        return self.__sendFunc(ResponseData(self.id, self.type, data=data))


    def __onDsData(self, datasource, *args):
        logger.debug("Datasource data (id %s; type %s): %s" % (self.id, self.type, datasource))
        
        # Only send partial response if secondaries do not
        # need to be calculated.
        if len(self.secondaries) == 0:
            #
            # TODO: this needs to be a seperate function, so as to be used by
            # partial responses and secondary responses
            #
            
            # Serialize panel data based on panel type.
            respData = datasource.panelTypeData(self.type)
            #logger.debug("====> Datapoints: %d" % (len(respData)))
            self.sendResponse(respData)



    def __onDsError(self, error, *args):
        logger.error(error)
        self.sendResponse(error.value.data)


    def __checkIfDone(self, *args):
        self.__activeSources -= 1
        if self.__activeSources == 0:
            #logger.info("Trigger request removal: %d" % (self.__activeSources))
            if len(self.secondaries) > 0:
                # TEMPORARY
                secDf = self.applySecondaries()
                # TODO: alias and serialize
                self.sendResponse({"error": "Secondaries need to be implemented!"})

            self.__panelRequestDone.callback(self.id)


    def cancel(self):
        for ds in self.datasources:
            ds.cancelRequest()


    def fetch(self, sendFunc):
        self.__sendFunc = sendFunc
        self.__panelRequestDone = defer.Deferred()
        
        for ds in self.datasources:
            # datasource deferred
            self.__activeSources += 1
            dfd = ds.fetch(**self._extraArgs)
            dfd.addCallbacks(self.__onDsData, self.__onDsError)
            dfd.addBoth(self.__checkIfDone)

        return self.__panelRequestDone

