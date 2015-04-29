"""
    Command line option parser
"""

import os
import sys
import logging

import metrilyx

from optparse import OptionParser

DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s %(name)s %(lineno)d] %(message)s"
LOG_BASENAME = "metrilyx-dataserver"

class DataserverOptionParser(OptionParser):

    def __init__(self, *args, **kwargs):
        OptionParser.__init__(self, *args, **kwargs)

        self.add_option("-l", "--log-level", dest="logLevel", default="INFO",
            help="Log level. (default: INFO)")
        self.add_option("--log-format", dest="logFormat", default=DEFAULT_LOG_FORMAT,
            help="Log output format. (default: '"+DEFAULT_LOG_FORMAT+"')")
        self.add_option("--log-dir", dest="logDir", default=None,
            help="Log directory.")

        self.add_option("--hostname", dest="hostname", default="localhost",
            help="Resolvable hostname  of the server. (default: localhost)")
        self.add_option("-p", "--port", dest="port", type="int", default=9000,
            help="Port to listen on. (default: 9000)")
        self.add_option("-e", "--external-port", dest="externalPort", type="int", default=None,
            help="External port if running behind a proxy such as nginx. This would be the port of the proxy, usually port 80.")

        self.add_option("--check-interval", dest="checkInterval", default=15.0, type="float", 
            help="Interval to check for process stats. (default: 15.0 secs)")
        self.add_option("--version", default=False, action="store_true")
        #self.add_option("--max-memory", dest="maxAllowedMemory", type="float", default=1500.0,
        #    help="Maximum allowed memory (MB) before server is gracefully respawned. (default: 1500.0 MB)")
    

    def __getLogger(self, opts):
        try:
            if opts.logDir != None:
                logFile = os.path.join(opts.logDir, LOG_BASENAME+"-"+str(opts.port)+".log")
                
                logging.basicConfig(filename=logFile,
                                    level=eval("logging.%s" % (opts.logLevel)), 
                                    format=opts.logFormat)
            else:
                logging.basicConfig(level=eval("logging.%s" % (opts.logLevel)), 
                                    format=opts.logFormat)
            
            return logging.getLogger(__name__)

        except Exception,e:
            print "[ERROR] %s" %(str(e))
            sys.exit(2)


    def parse_args(self, args=None, values=None):
        opts, args = OptionParser.parse_args(self)
        
        if opts.version:
            print metrilyx.version
            sys.exit(0)

        setattr(opts, "logger", self.__getLogger(opts))
        opts.logger.warning("* Log level: %s" % (opts.logLevel))
        
        return (opts, args)

