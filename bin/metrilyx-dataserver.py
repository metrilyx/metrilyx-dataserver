#!/usr/bin/env python

import sys
import resource

from pprint import pprint

#from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import listenWS

from metrilyx.server.websock import WSFactory
from metrilyx.server.protocol import PanelRequestProtocol
from metrilyx.cli import DataserverOptionParser


def getMemUsage():
    """
        Get memory usage for the calling process.

        Return:
            memory consumption for calling process in MB's.
    """
    rusage_denom = 1024.00
    if sys.platform == 'darwin':
        # OS X unit is KB
        rusage_denom = rusage_denom * rusage_denom     
    
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / rusage_denom


def checkMemory(checkInterval):
    """ Get memory usage and schedule next check """

    print "* ==> Memory: %f MBs" % (getMemUsage())
    reactor.callLater(checkInterval, checkMemory, checkInterval)


if __name__ == "__main__":
    
    parser = DataserverOptionParser()
    (opts, args) = parser.parse_args()
    
    #log.startLogging(sys.stdout)

    factory = WSFactory(opts.logger, "ws://%s:%d" % (opts.hostname, opts.port), 
                                                    externalPort=opts.externalPort)
    # Set protocol with compression support.
    factory.setProtocol(PanelRequestProtocol)


    checkMemory(opts.checkInterval)


    listenWS(factory)
    reactor.run()

