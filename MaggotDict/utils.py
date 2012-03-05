# -*- coding: utf-8 -*-

__all__ = ('Disposable', 'CompositeDisposable', 'Event',)
#-----------------------------------------------------------------------------#
# Disposable                                                                  #
#-----------------------------------------------------------------------------#
class Disposable (object):
    __slots__ = ('dispose')
    def __init__ (self, dispose = None):
        self.dispose = dispose

    def __enter__ (self):
        return self

    def __exit__ (self, et, eo, tb):
        if self.dispose is not None:
            self.dispose ()
            self.dispose = None
        return False

    def __bool__ (self):
        return self.dispose is not None

    def Dispose (self):
        if self.dispose is not None:
            self.dispose ()
            self.dispose = None

#-----------------------------------------------------------------------------#
# Composite Disposable                                                        #
#-----------------------------------------------------------------------------#
class CompositeDisposable (object):
    __slots__ = ('disposed', 'disposables')

    def __init__ (self, *disposables):
        self.disposables = set ()
        try:
            for disposable in disposables:
                disposable.__enter__ ()
                self.disposables.add (disposable)
        except:
            for disposable in disposables:
                disposable.__exit__ (None, None, None)
            raise
        self.disposed = False

    def __iadd__ (self, disposable):
        disposable.__enter__ ()
        if self.disposed:
            disposable.__exit__ (None, None, None)
        else:
            self.disposables.add (disposable)
        return self

    def __isub__ (self, disposable):
        self.disposables.remove (disposable)
        disposable.__exit__ ()
        return self

    def __enter__ (self):
        return self

    def __exit__ (self, et, eo, tb):
        self.Dispose ()
        return False

    def __bool__ (self):
        return not self.disposed

    def Dispose (self):
        if self.disposed:
            return
        self.disposed = True
        for disposable in self.disposables:
            disposable.__exit__ (None, None, None)
        self.disposables.clear ()

#-----------------------------------------------------------------------------#
# Event                                                                       #
#-----------------------------------------------------------------------------#
class Event (object):
    """Simple Event implementation"""
    __slots__ = ('__handlers',)

    def __init__ (self):
        self.__handlers = set ()

    def __call__ (self, *args, **keys):
        for handler in self.__handlers:
            handler (*args, **keys)

    def __iadd__ (self, handler):
        self.__handlers.add (handler)
        return self

    def __isub__ (self, handler):
        self.__handlers.discard (handler)
        return self

# vim: nu ft=python columns=120 :
