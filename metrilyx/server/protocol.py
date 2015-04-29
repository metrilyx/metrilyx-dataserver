
import ujson as json

from websock import PanelRequestParserWSProto
from request_tracker import RequestTracker

from pprint import pprint

class PanelRequestProtocol(PanelRequestParserWSProto):

    reqTracker = RequestTracker()


    def __onRequestDone(self, _id):
        self.reqTracker.removeRequest(_id)


    def onPanelData(self, respData):
        self.factory.logger.debug("Sending: %s" % (respData.id))
        self.sendMessage(json.dumps(respData))


    def onPanelRequest(self, panelRequest):
        self.reqTracker.addRequest(panelRequest)
        self.factory.logger.debug("Panel request: %s" % (panelRequest.id))
        
        # Start fetching. Pass in function to send data with.
        d = panelRequest.fetch(self.onPanelData)
        d.addCallback(self.__onRequestDone)
        
        # Print panel request
        jStr = json.dumps(panelRequest)
        pprint(json.loads(jStr))


    def onTearDown(self):
        self.reqTracker.cancelActiveRequests()