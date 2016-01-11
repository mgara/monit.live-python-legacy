from abc import ABCMeta, abstractmethod

'''
This interface is the base class for the EventSettings
'''


class IEventSettingsInterface(metaclass=ABCMeta):


    '''
    this function takes as a parametr the event object and will 
    indicate how to process the event
    '''

    @abstractmethod
    def process(self, event_object):
        raise

    '''
    this function will be called when the process is done
    '''

    @abstractmethod
    def finalize(self, event_object):
        pass
