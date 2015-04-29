import uuid

class UUID(object):

    def __init__(self):
        self.__uuid = uuid.uuid4()

    def __str__(self):
        return "".join(str(self.__uuid).split("-"))