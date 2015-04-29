

class IProvider(object):

    def normalizedAlias(self, metaStr, aliasStr):
        raise NotImplementedError("Subclass must implement this method!")

    def aggr(self):
        raise NotImplementedError("Subclass must implement this method!")
