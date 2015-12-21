from abc import ABCMeta, abstractmethod



    '''
    This interface is to implement Event Settings
    '''
class IEventSettingsInterface(metaclass=ABCMeta):
    
    def __init__(self, name=None, **opts):
        self.name = name
        for key, value in opts.items():
            setattr(self, key, value)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    '''
    this function takes as a parametr the event object and will 
    indicate how to process the event
    '''
    @abstractmethod
    def process(self,event_object):
        raise 

    '''
    this function will be called when the process is done
    '''
    @abstractmethod
    def finalize(self,event_object):
        pass
