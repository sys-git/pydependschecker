'''
Created on 19 Feb 2013

@author: francis
'''

class DependencyException(Exception):
    pass

class NoRootException(DependencyException):
    pass

class CircularDependencyException(DependencyException):
    def __init__(self, item, offender):
        self._item = item
        self._offender = offender
        super(CircularDependencyException, self).__init__()
    def getOffender(self):
        return self._offender.uId()
    def uId(self):
        return self._item.uId()
    def __str__(self):
        s = []
        s.append("Offender: %(O)s, referenced from: %(W)s"%{"W":self.uId(), "O":self.getOffender()})
        return " ".join(s)

class SelfDependencyException(DependencyException):
    def __init__(self, item):
        self._item = item
        super(SelfDependencyException, self).__init__()
    def uId(self):
        return self._item.uId()
    def __str__(self):
        s = []
        s.append("Offender: %(O)s"%{"W":self.uId()})
        return " ".join(s)

class UnsatisfiedDependencyException(DependencyException):
    def __init__(self, item, dependency):
        super(UnsatisfiedDependencyException, self).__init__()
        self._item = item
        self._dependency = dependency
    def uId(self):
        return self._item.uId()
    def getOffender(self):
        try:
            return self._dependency.uId()
        except:
            return self._dependency
    def __str__(self):
        s = []
        s.append("Offender: %(O)s, referenced from: %(W)s"%{"W":self.uId(), "O":self.getOffender()})
        return " ".join(s)
