
class ResponseData(object):

    def __init__(self, _id, _type, **kwargs):
        self.id = _id
        self.type = _type
        
        if type(kwargs["data"]) not in (list, tuple, dict):
            raise RuntimeError("Invalid data type. Must be a list or tuple!")
        
        self.data = kwargs["data"]
