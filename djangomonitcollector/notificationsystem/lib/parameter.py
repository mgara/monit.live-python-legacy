__author__ = 'mehergara'


class Parameter(object):

    """
    Type can be a str / choices
    """

    def __init__(self, id, label, value="", _help_block=None, _choices=None):
        self.__id = id
        self.__label = label
        self.__value = value
        self.__choices = _choices
        self.__help_block = _help_block

    @property
    def help_block(self):
        return self.__help_block

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
