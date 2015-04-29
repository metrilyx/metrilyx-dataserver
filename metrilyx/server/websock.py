
import ujson as json

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from autobahn.websocket.compress import PerMessageDeflateOffer, PerMessageDeflateOfferAccept

from pprint import pprint

from ..schema.panel import PanelRequest

## Enable WebSocket extension "permessage-deflate".
## Function to accept offers from the client ..
def acceptedCompression(offers):
    for offer in offers:
        if isinstance(offer, PerMessageDeflateOffer):
            return PerMessageDeflateOfferAccept(offer)


class WSFactory(WebSocketServerFactory):
    """ Basic websocket factory that keeps track of clients. """

    def __init__(self, logger, *args, **kwargs):
        WebSocketServerFactory.__init__(self, *args, **kwargs)
        self.logger = logger
        self.clients = []

    def setProtocol(self, proto):
        self.protocol = proto
        self.setProtocolOptions(perMessageCompressionAccept=acceptedCompression)

    def addClient(self, client):
        self.clients.append(client)
        self.logger.info("Clients: %d" % (len(self.clients)))

    def removeClient(self, client):
        self.clients.remove(client)
        self.logger.info("Clients: %d" % (len(self.clients)))


class PanelRequestParserWSProto(WebSocketServerProtocol):
    """ Parse raw websocket data into PanelRequest object """

    def sendJSON(self, obj):
        """ Helper function """
        self.sendMessage(json.dumps(obj), False)

    def parsePanelRequest(self, payload):
        """ 
            Decode and parse websocket payload into PanelRequest object
        """
        try:
            payloadDict = json.loads(payload.decode('utf8'))
            preq = PanelRequest(**payloadDict)
            if len(preq.datasources) <= 0:
                return None
            else:
                return preq
        except Exception, e:
            self.factory.logger.error("Failed to parse panel request: %s" % (e))
            self.sendJSON({
                "error": "Failed to parse request: %s" % str(e),
                "data": payloadDict
                })
            return None

    def onConnect(self, request):
        self.factory.addClient(self)
        self.factory.logger.info("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        self.factory.logger.debug("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            self.factory.logger.warning("Binary message received (not supported): {0} bytes".format(len(payload)))
        else:
            panelReq =  self.parsePanelRequest(payload)
            # Error
            if panelReq == None:
                return

            self.onPanelRequest(panelReq)


    def onClose(self, wasClean, code, reason):
        self.factory.logger.info("WebSocket connection closed: {0}".format(reason))
        # Call user cleanup if provided.
        self.onTearDown()
        self.factory.removeClient(self)

    def onTearDown(self):
        """ Called before client connection is removed """
        pass

    def onPanelRequest(self, panelRequest):
        """ This is what the subclass needs to implement """
        pass
