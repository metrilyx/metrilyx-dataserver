
import logging

import aliasing
import serializer

logger = logging.getLogger(__name__)

class SecondaryMetric(serializer.ISerializer):

    def __init__(self, alias, operation, aggregator='sum'):
        self.alias = alias
        self.operation = operation
        self.aggregator = aggregator

    def aggr(self):
        return self.aggregator

    def applyOperation(self, dss):
        """
        Args:
            dss : DataFrame datasource data
        """
        try:
            logger.debug("Secondary operation: " + self.operation)
            rslt = eval(self.operation)(*dss)
            # set id
            rslt.columns = [ aliasing.getLambdaContent(self.operation) + r 
                                            for r in rslt.columns.values ]
            setattr(self, 'data', rslt)
        except Exception, e:
            logger.error("Failed to apply secondary operation: %s" %(e))
            setattr(self, 'data', { "error": "Secondary operation failed: %s" % (e) })

