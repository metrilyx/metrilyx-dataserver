
import time

from twisted.internet import reactor
import logging

logger = logging.getLogger(__name__)


class TrackedRequest(object):
    def __init__(self, panelReq):
        self.timestamp = time.time()
        self.request = panelReq


class RequestTracker(object):
    """
        Track panel requests and expire ones that have been running for
        too long.
    """
    def __init__(self, *args, **kwargs):
        self.activeRequests = {}
        self.requestTimeout = 600
        # start expirer
        reactor.callLater(self.requestTimeout, self.removeTimeoutRequests)

    def removeTimeoutRequests(self):
        logger.info("Expiring requests...")
        expireTime = time.time() - self.requestTimeout

        for k, v in self.activeRequests.items():
            if v.timestamp < expireTime:
                v.request.cancel()
                self.removeRequest(k)

        # may need to save this deferred ??
        reactor.callLater(self.requestTimeout, self.removeTimeoutRequests)


    def addRequest(self, panelReq):
        """
            Add request to tracker and start fetching data.

            Returns:
                True if added False if not
        """
        if not self.activeRequests.has_key(panelReq.id):
            self.activeRequests[panelReq.id] = TrackedRequest(panelReq)
            logger.info("Active requests (added): %d" % (len(self.activeRequests.keys())))
            return True
        else: 
            logger.warning("Active request duplicate id (not adding): %s" % (panelReq.id))
            return False


    def removeRequest(self, _id):
        if self.activeRequests.has_key(_id):
            # check if active before removing
            del self.activeRequests[_id]
            logger.info("Active requests (removed): %d" % (len(self.activeRequests.keys())))
        else:
            logger.warning("Active request not found: %s" % (_id))

    def cancelActiveRequests(self):
        for k, v in self.activeRequests.items():
            v.request.cancel()
            self.removeRequest(k)