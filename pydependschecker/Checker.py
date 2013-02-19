'''
Created on 19 Feb 2013
@summary: Checks hierarchical dependency graphs in the form [(int_id, [dependency_int_ids])].

@author: Francis
'''

from pydependschecker.Errors import UnsatisfiedDependencyException, \
    NoRootException, SelfDependencyException, CircularDependencyException
from sets import Set
from threading import RLock
import copy

class _DependantItem(object):
    def __init__(self, uId, dependancies=[]):
        self._uId = uId
        self.setDependencies(dependancies)
    def uId(self):
        return self._uId
    def setDependencies(self, dependancies):
        self._dependancies = dependancies
    def dependancies(self):
        return self._dependancies
    def numDependancies(self):
        return len(self._dependancies)

class Checker(object):
    r"""
    @summary: Use this class to check a dependency tree of uIds. Checks for self, unsatisfied and circular references as well as (optionally)
    whether any uIds have no dependencies.
    """
    @staticmethod
    def _findUid(uId, items):
        for i in items:
            if i.uId()==uId:
                return i
    @staticmethod
    def _checkItems(_items, checkNoRoot=True):
        if (_items is None) or (len(_items)==0):
            raise ValueError("Expecting some items to check: %(I)s"%{"I":_items})
        newItems = []
        keys = {}
        for i in _items:
            if i is not None:
                try:
                    (j, k) = i
                except:
                    j = i
                    k = []
                if j in keys.keys():
                    raise ValueError("item uId %(V)s specified more than once!"%{"V":i})
                if not isinstance(j, int):
                    raise ValueError("item uId %(V)s is not of correct type: %(E)s"%{"V":i, "E":int})
                if k is not None:
                    if not isinstance(k, list):
                        raise ValueError("item dependencies %(V)s are not of correct type: %(E)s"%{"V":i, "E":list})
                keys[j]=k
                newItems.append((j, k))
        del keys
        nItems = copy.deepcopy(newItems)
        #    Now create a list of _DependantItems for each item in _items, 2 passes: 1. Create the primaries, 2. Link the dependencies:
        items = []
        #    Pass1:
        for i in nItems:
            (j, k)=i
            items.append(_DependantItem(j, k))
        #    Pass2:
        for i in items:
            d = i.dependancies()
            newDependencies = []
            for k in d:
                aDependency = Checker._findUid(k, items)
                if aDependency is not None:
                    newDependencies.append(aDependency)
                else:
                    raise UnsatisfiedDependencyException(i, k)
            i.setDependencies(newDependencies)
        #    Now check we have no resultant items:
        if len(items)==0:
            raise ValueError("Expecting some items to check: %(I)s"%{"I":_items})
        #    Determine the uIds with no dependencies:
        noDependencies = []
        for i in items:
            if i.numDependancies()==0:
                noDependencies.append(i)
        #    First check: noDependents>0:
        if (len(noDependencies)==0) and (checkNoRoot is True):
            raise NoRootException()
        #    Determine the uIds with dependencies:
        for i in noDependencies:
            items.remove(i)
        allItems = copy.deepcopy(noDependencies)
        allItems.extend(copy.deepcopy(items))
        return (allItems, (noDependencies, items))
    @staticmethod
    def _check(root, allItems, currentItem, currentHierarchy, allHierarchies):
        cUid = currentItem.uId()
        dependencies = currentItem.dependancies() #1, #2
        if len(dependencies)==0:
            if len(currentHierarchy)>0:
                if currentHierarchy not in allHierarchies:
                    allHierarchies.append(copy.deepcopy(currentHierarchy))
        for i in dependencies:
            #    1.    Check that the dependency isn't it's self:
            dUid = i.uId()
            if cUid==dUid:
                raise SelfDependencyException(currentItem)
            #    2.    Check that the dependency isn't in our hierarchy already:
            if dUid in currentHierarchy:
                raise CircularDependencyException(currentItem, i)
            #    3.    Check that the dependency exists!
            fUid = Checker._findUid(dUid, allItems)
            if fUid is None:
                raise UnsatisfiedDependencyException(currentItem, i)
            #    Dependency is valid...
            currentHierarchy.append(dUid)
            #    ...so check it:
            Checker._check(root, allItems, i, currentHierarchy, allHierarchies)
            currentHierarchy.pop()
        #    All dependencies satisfied!
        pass
    @staticmethod
    def verify(_items, checkNoRoot=True):
        r"""
        @summary: Verify the input dependency hierarchy.
        Dependencies are referenced by 'uId' (a unique integer for each item in the tree)
        @param _items: A list of tuples(UID, [dependency_UIDS_for_this_UID])
        @param checkNoRoot: True=Raise NoRootException is there are no uIds with no dependencies. False=otherwise.
        @return: tuple(independentsUids, allHierarchies, dependencyMap)
        @raise ValueError: Incorrectly specified input data.
        @raise exception: UnsatisfiedDependencyException
        @raise exception: NoRootException
        @raise exception: SelfDependencyException
        @raise exception: CircularDependencyException
        @note: eg: verify([(1,[]), (2,[1]), (3,[3,6])])
                ie: '1' depends on nothing.
                    '2' depends on [1]
                    '3' depends on [3 and 6].
        """
        #    First check the inputs:
        (allItems, (independents, items)) = Checker._checkItems(_items, checkNoRoot)
        #    Now do the verify, iterate over the items with dependencies:
        allHierarchies = []
        for root in items:
            currentItem = root
            cId = currentItem.uId()
            currentHierarchy = [cId]
            if cId==13:
                pass
            Checker._check(root, allItems, currentItem, currentHierarchy, allHierarchies)
        iUids = []
        for i in independents:
            uId = i.uId()
            iUids.append(uId)
            allHierarchies.insert(0, [uId])
        #    Now collapse the hierarchies and produce a dependencyMap:
        dependencyMap = Checker._createDependencyMap(allHierarchies)
        return Checker(allHierarchies, dependencyMap)
    @staticmethod
    def _createDependencyMap(allHierarchies):
        r"""
        @summary: Collapse all hierarchies to a single dependency map.
        """
        if allHierarchies is None:
            raise ValueError("Expecting some hierarchies to collapse!")
        routes = {}
        for i in allHierarchies:
            key = i[0]
            if key not in routes.keys():
                routes[key] = {}
            routes[key].update(dict.fromkeys(i[1:], None))
        theMap = []
        for key, values in routes.items():
            theMap.append((key, values.keys()))
        return theMap
    @staticmethod
    def maxDepth(allHierarchies):
        r"""
        @summary: Get the max depth of all hierarchies.
        @param allHierarchies: The previously generated list of hierarchies returned from Checker.verify().
        @return: type=int, the max length of any hierarchy.
        @raise ValueError: No hierarchies specified!
        """
        if allHierarchies is None:
            raise ValueError("No hierarchies list specified!")
        _len = 0
        for i in allHierarchies:
            if not isinstance(i, list):
                raise ValueError("Hierarchies incorrectly specified: %(L)s"%{"L":i})
            _len=max(_len, len(i))
        return _len
    @staticmethod
    def applyMapping(dependencyMap, mapItems):
        r"""
        @summary: Map the mapItems into the dependencyMap and return a new map of items from mapItems.
        @param: A dependency map as returned by Checker.verify().
        @param mapItems: A dict mapping (uId to item).
        @raise ValueError: No dependencyMap specified.
        @raise ValueError: No mapItems specified or mapItems is not of type dict.
        """
        if dependencyMap is None or not isinstance(dependencyMap, list):
            raise ValueError("No dependencyMap list(tuple(key, dependencies)) specified!")
        if mapItems is None or not isinstance(mapItems, dict):
            raise ValueError("No mapItems dict specified!")
        result = []
        for i in dependencyMap:
            (key, values) = i
            items = map(lambda(x): mapItems[x], values)
            result.append((key, items))
        return result
    def __init__(self, allHierarchies=[], dependencyMap=[]):
        self._lock = RLock()
        self._allHierarchies = allHierarchies
        self._dependencyMap = dependencyMap
        self._satisfied = []
        self._pending = []
    def getIndependents(self):
        with self._lock:
            roots = []
            for i in self._dependencyMap:
                if len(i[1])==0:
                    roots.append(i[0])
            remainingRoots = Set(roots) - Set(self._pending)
            if len(remainingRoots)==0:
                raise NoRootException()
            return list(remainingRoots)
    def getallHierarchies(self):
        with self._lock:
            return copy.deepcopy(self._allHierarchies)
    def getDependencyMap(self):
        with self._lock:
            return copy.deepcopy(self._dependencyMap)
    def getSatisfied(self):
        with self._lock:
            return frozenset((tuple(self._satisfied)))
    def getPending(self):
        with self._lock:
            return frozenset((tuple(self._pending)))
    def getMaxDepth(self):
        with self._lock:
            return Checker.maxDepth(self.allHierarchies)
    independents = property(getIndependents)
    allHierarchies = property(getallHierarchies)
    dependencyMap = property(getDependencyMap)
    satisfied = property(getSatisfied)
    pending = property(getPending)
    depthMax = property(getMaxDepth)
    def next(self):
        r"""
        @summary: Return the next independent:
        """
        with self._lock:
            uId = self.independents[0]
            self._pending.append(uId)
            return uId
    def recycle(self, uId):
        r"""
        @summary: A uId was not satisfied, put it back in the independents:
        """
        with self._lock:
            self._pending.remove(uId)
    def satisfy(self, uInt):
        r"""
        @summary: A dependency has been satisfied, mark it as such.
        """
        #    Remove this uInt as a dependency on other uIds:
        with self._lock:
            try:
                self._pending.remove(uInt)
            except Exception, _e:
                #    Don't care
                pass
            toRemove = []
            for index, i in enumerate(self._allHierarchies):
                try:
                    i.remove(uInt)
                    if len(i)==0:
                        toRemove.append(index)
                except Exception, _e:
                    pass
            toRemove.reverse()
            for i in toRemove:
                self._allHierarchies.pop(i)
            #    Now flatten the remaining hierarchies:
            keys = {}
            for i in self._allHierarchies:
                keys[frozenset((tuple(i)))] = None
            k = keys.keys()
            k.sort()
            hierarchies = []
            for l in k:
                hierarchies.append(list(l))
            self._allHierarchies = hierarchies
            for i in self._dependencyMap:
                try:
                    i[1].remove(uInt)
                except Exception, _e:
                    pass
            #    Remove this satisfied uInt:
            for index, i in enumerate(self._dependencyMap):
                if i[0]==uInt:
                    self._dependencyMap.pop(index)
                    self._satisfied.append(i[0])
                    break

