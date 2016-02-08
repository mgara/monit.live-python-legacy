__author__ = 'mehergara'


class Parameter(object):

    def __init__(self, id, label, value=""):
        self.__id = id
        self.__label = label
        self.__value=value


    @property
    def id(self):
        return self.__id

    @property
    def label(self):
        return self.__label

    @property
    def value(self):
        return self.__value


    def __str__(self):
        return self.__id