# -*- test-case-name: test.test_websock -*-

import ujson as json

from websock import WSFactory, PanelRequestParserWSProto

from schema import panel

from twisted.trial import unittest

from twisted.test import proto_helpers



testWebsockUri = "ws://127.0.0.1:9000"

testPanelRequestError = json.dumps({
    "id": "1234567890abcdefg",
    "name": "test panel request",
    "type": "text",
    "datasources": [],
    "secondaries": [],
    "size": "medium" 
    })

testPanelRequest = json.dumps({
    "id": "1234567890abcdefg",
    "name": "test panel request",
    "type": "text",
    "datasources": [{
        "type": "http",
        "provider": {
            "name": "http",
            "url": "",
            "method": "GET",
            "params": "",
            "body": ""
            },
        "transform": "",
        "alias": ""
        }],
    "secondaries": [],
    "size": "medium" 
    })


class PanelRequestParserWSProtoTest(unittest.TestCase):
    
    def setUp(self):
        factory = WSFactory(testWebsockUri)
        factory.setProtocol(PanelRequestParserWSProto)
        # need for testing since there's no real connection
        factory.openHandshakeTimeout = None
        
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_parsePanelRequest_error(self):
        
        panelReq = self.proto.parsePanelRequest(testPanelRequestError)
        self.assertEqual(panelReq, None)


    def test_parsePanelRequest(self):
        
        panelReq = self.proto.parsePanelRequest(testPanelRequest)
        self.assertEqual(type(panelReq), panel.PanelRequest)
