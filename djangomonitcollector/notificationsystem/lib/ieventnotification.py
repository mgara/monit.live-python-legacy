from abc import ABCMeta, abstractmethod
import ast

'''
This interface is the base class for the EventSettings
'''


class IEventSettingsInterface(object):
    __metaclass__ = ABCMeta

    extra_params = dict()
    event = None

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


    def set_event(self,event_object):
        self.event = event_object

    def set_extra_params(self,extra_params):
        if extra_params:
            if len(extra_params)>0:
                self.extra_params = ast.literal_eval(extra_params)
                return
        self.extra_params = None