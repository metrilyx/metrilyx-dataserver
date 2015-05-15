
import numpy
import logging

import aliasing

PANEL_TYPES_NONTS = ("bar", "column", "pie")

logger = logging.getLogger(__name__)

class ISerializer(object):

    def aggr(self):
        raise NotImplementedError("Subclass must implement this method!")


def columnToDatapoints(column):
    """
        Convert pandas.DataFrame column to datapoints.

        Return:
            A list of 2 elem tuples.
    """
    nonNanSerie = column.replace([numpy.inf, -numpy.inf], numpy.nan).dropna()
    # convert timestamp to milliseconds
    tsIdx = nonNanSerie.index.astype(numpy.int64)/1000000
    # re-combine timestamps and value for the column and return [(...)]
    return zip(tsIdx, nonNanSerie.values)


def serializeNonTsTypes(dstruct):
    out = []
    for colname in dstruct.data:
        nAlias = aliasing.DataAlias(dstruct.alias, colname).alias()
        
        cleanCol = dstruct.data[colname].replace([numpy.inf, -numpy.inf], numpy.nan).dropna()
        
        if dstruct.aggr() == "avg":
            out.append({
                "id": colname,
                "alias": nAlias,
                "data": cleanCol.mean()
            })
        else:
            out.append({
                "id": colname,
                "alias": nAlias,
                "data": eval("cleanCol.%s()" % (dstruct.aggr()))
            })

    return out


def serialize(dstruct, panelType):
    """
        Serialize data based on panel type.  All graph types must be of 
        type pandas.DataFrame

        Args:
            dstruct : Datasource, SecondaryMetric

        Return:
            list : Serialized data based on panel type

    """

    logger.debug("Serializing: %s" %(type(dstruct)))

    if panelType == "list":
        
        return [{
            "id": "",
            "alias": dstruct.alias,
            "data": it,
        } for it in dstruct.data ]

    elif panelType == "text":
        
        return {
            "id": "",
            "alias": dstruct.alias,
            "data": dstruct.data
            }

    elif panelType in PANEL_TYPES_NONTS:
        # Serialize non-timeseries graphs
        return serializeNonTsTypes(dstruct)
    else:
        # Time Series data.
        return [{
            "alias": aliasing.DataAlias(dstruct.alias, col).alias(),
            "id": col,
            "data": columnToDatapoints(dstruct.data[col])
            } for col in dstruct.data.columns ]
