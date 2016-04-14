__author__ = 'mehergara'


class Parameter(object):
    """
    Type can be a str / choices
    """
    def __init__(self, id, label, value="", _choices=None):
        self.__id = id
        self.__label = label
        self.__value = value
        self.__choices = _choices

    @property
    def id(self):
        return self.__id

    @property
    def label(self):
        return self.__label

    @property
    def choices(self):
        return self.__choices

    @property
    def value(self):
        return self.__value

    def __str__(self):
        return self.__id
