"""
    Command line parser
"""

import os
import sys
import logging

from twisted.python import log

import metrilyx

from optparse import OptionParser
import argparse


DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s %(name)s %(lineno)d] %(message)s"
LOG_BASENAME = "metrilyx-dataserver"

class DataserverOptionParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):

        super(DataserverOptionParser, self).__init__(*args, **kwargs)

        self.add_argument("-l", "--log-level", dest="logLevel", default="INFO",
            help="Log level (default: INFO). [error|warning|info|debug|trace]")
        self.add_argument("--log-dir", dest="logDir", default=None,
            help="Log directory.")

        self.add_argument("--hostname", dest="hostname", default="localhost",
            help="Resolvable hostname or ip address of the server. (default: localhost)")
        self.add_argument("-p", "--port", dest="port", type=int, default=9000,
            help="Port to listen on. (default: 9000)")
        self.add_argument("-e", "--external-port", dest="externalPort", type=int, default=None,
            help="External port if running behind a proxy such as nginx. This would be the port of \
            the proxy, usually port 80.")

        self.add_argument("-c", "--check-interval", dest="checkInterval", default=300.0, type=float, 
            help="Interval to check for process stats. (default: 5 mins)")
        self.add_argument("-V", "--version", default=False, action="store_true",
            help="Show version.")


    def __getLogger(self, opts):
        opts.logLevel = opts.logLevel.upper()
        try:
            logOpts = { "format": DEFAULT_LOG_FORMAT }
            
            if opts.logLevel == "TRACE":
                log.startLogging(sys.stdout)
                logOpts["level"] = logging.DEBUG
            else:
                logOpts["level"] = eval("logging.%s" % (opts.logLevel))

            if opts.logDir != None:
                logOpts["filename"] = os.path.join(opts.logDir, LOG_BASENAME+"-"+str(opts.port)+".log")


            logging.basicConfig(**logOpts)
            return logging.getLogger(__name__)

        except Exception,e:
            print "[ERROR] %s" %(str(e))
            sys.exit(2)


    def parse_args(self, args=None, namespace=None):
        
        opts = super(DataserverOptionParser, self).parse_args(args=args, namespace=namespace)

        if opts.version:
            print metrilyx.version
            sys.exit(0)

        setattr(opts, "logger", self.__getLogger(opts))
        opts.logger.warning("* Log level: %s" % (opts.logLevel))
        
        return opts

