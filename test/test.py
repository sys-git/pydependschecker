'''
Created on 19 Feb 2013

@author: Francis
'''

from pydependschecker import Checker, NoRootException, \
    CircularDependencyException, SelfDependencyException, \
    UnsatisfiedDependencyException
import itertools
import traceback
import unittest

class Test(unittest.TestCase):
    def setUp(self):
        self.id = itertools.count(1)
    def testHappyPath(self):
        items = []
        numIndependants = 3
        numUnsatisfied = 0
        indis = []
        for _i in range (0, numIndependants):
            indis.append((self.id.next()))        #1-3
        items.extend(indis)
        items.append((self.id.next(), [1,2]))     #4
        items.append((self.id.next(), [1,4]))     #5
        items.append((self.id.next(), [1,3,4]))   #6
        eMaxDepth = 3
        unsat = []
        unsats = []
        for _i in range(0, numUnsatisfied):
            id_ = self.id.next()
            unsats.append(id_)
            unsat.append((id_, [1000+_i]))
        items.extend(unsat)
        try:
            dc = Checker.verify(items)
        except Exception, _e:
            raise
        else:
            assert len(dc.independents)==numIndependants, "Expecting %(N)s independents but found %(F)s:\r\n%(E)s"%{"F":len(dc.independents), "N":len(numIndependants)}
            dc.independents.sort()
            indis.sort()
            #    Check the independents:
            assert dc.independents==indis, "Different independent uIds: %(A)s to that expected: %(E)s"%{"A":dc.independents, "E":indis}
            #    Check the maxDepth:
            maxDepth = Checker.maxDepth(dc.allHierarchies)
            depth = dc.depthMax
            assert maxDepth==depth
            assert maxDepth==eMaxDepth, "Max depth: %(A)s is different to that expected: %(E)s"%{"A":maxDepth, "E":eMaxDepth}
            return (items, dc.independents, dc.allHierarchies, dc.dependencyMap)
    def testUnsatisfiedDependency(self):
        items = []
        numIndependants = 3
        numUnsatisfied = 6
        indis = []
        for _i in range (0, numIndependants):
            indis.append((self.id.next()))        #1-3
        items.extend(indis)
        items.append((self.id.next(), [1,2]))     #4
        items.append((self.id.next(), [1,4]))     #5
        items.append((self.id.next(), [1,3,4]))   #6
        items.append((self.id.next(), [2,8]))     #7
        unsat = []
        unsats = []
        for _i in range(0, numUnsatisfied):
            id_ = self.id.next()
            unsats.append(id_)
            unsat.append((id_, [1000+_i]))
        items.extend(unsat)
        try:
            Checker.verify(items)
        except CircularDependencyException, e:
            assert False, "No circular dependencies expected:\r\n%(E)s\r\n%(T)s"%{"E":e, "T":traceback.format_exc()}
        except UnsatisfiedDependencyException, e:
            #    Check the unsatisfied:
            uId = e.uId()
            offender = [e.getOffender()]
            assert uId in unsats, "uId %(U)s not in list of expected unsatisfieds: %(F)s :\r\n%(T)s"%{"F":unsat, "U":uId, "T":traceback.format_exc()}
            for i in unsat:
                (eUid, eOffender) = i
                if uId==eUid:
                    assert offender==eOffender, "Offender is incorrect, expecting: %(E)s, found: %(A)s."%{"E":offender, "A":eOffender}
        else:
            assert False, "No unsatisfied dependencies found!"
    def testCircularDependeny(self):
        items = []
        numIndependants = 3
        numUnsatisfied = 0
        indis = []
        for _i in range (0, numIndependants):
            indis.append((self.id.next()))        #1-3
        items.extend(indis)
        items.append((self.id.next(), [1,2]))     #4
        items.append((self.id.next(), [1,4]))     #5
        items.append((self.id.next(), [1,3,4]))   #6
        offenders = []
        id_ = self.id.next()
        offenders.append(id_)
        items.append((id_, [2,8]))     #7
        #    Circular dependency 'Offender':
        id_ = self.id.next()
        offenders.append(id_)
        items.append((id_, [6,7]))     #8
        unsat = []
        unsats = []
        for _i in range(0, numUnsatisfied):
            id_ = self.id.next()
            unsats.append(id_)
            unsat.append((id_, [1000+_i]))
        items.extend(unsat)
        try:
            Checker.verify(items)
        except CircularDependencyException, e:
            offender = e.getOffender()
            assert offender in offenders, "Expecting circular offender: %(N)s not in offenders list: %(E)s\r\n%(T)s"%{"N":offender, "E":offenders}
        else:
            assert False, "Circular dependencies expected!"
    def testSelfDependeny(self):
        items = []
        numIndependants = 3
        numUnsatisfied = 0
        indis = []
        for _i in range (0, numIndependants):
            indis.append((self.id.next()))        #1-3
        items.extend(indis)
        items.append((self.id.next(), [1,2]))     #4
        items.append((self.id.next(), [1,4]))     #5
        items.append((self.id.next(), [1,3,4]))   #6
        items.append((self.id.next(), [2,8]))     #7
        #    Self dependency 'Offender':
        id_ = self.id.next()
        offender = id_
        items.append((id_, [6,8]))     #8
        unsat = []
        unsats = []
        for _i in range(0, numUnsatisfied):
            id_ = self.id.next()
            unsats.append(id_)
            unsat.append((id_, [1000+_i]))
        items.extend(unsat)
        try:
            Checker.verify(items)
        except SelfDependencyException, e:
            uId = e.uId()
            assert uId==offender, "Expecting Self offender: %(N)s."%{"N":offender}
        else:
            assert False, "Self dependencies expected:\r\n%(T)s"%{"T":traceback.format_exc()}
    def testComplex(self):
        items = []
        numIndependants = 1
        numUnsatisfied = 0
        indis = []
        for _i in range (0, numIndependants):
            indis.append((self.id.next()))                  #1
        items.extend(indis)
        items.append((self.id.next(), [1]))                 #2
        items.append((self.id.next(), [1]))                 #3
        items.append((self.id.next(), [1,2]))               #4
        items.append((self.id.next(), [2,3]))               #5
        items.append((self.id.next(), [3]))                 #6
        items.append((self.id.next(), [4,5]))               #7
        items.append((self.id.next(), [4,6]))               #8
        items.append((self.id.next(), [4,5,6]))             #9
        items.append((self.id.next(), [7,8]))               #10
        items.append((self.id.next(), [10]))                #11
        items.append((self.id.next(), [2,7,10]))            #12
        endId = self.id.next()
        items.append((endId, [1,2,4,9,10,11,12]))  #13
        eMaxDepth = 7
        unsat = []
        unsats = []
        for _i in range(0, numUnsatisfied):
            id_ = self.id.next()
            unsats.append(id_)
            unsat.append((id_, [1000+_i]))
        items.extend(unsat)
        try:
            dc = Checker.verify(items)
        except Exception, _e:
            raise
        else:
            assert len(dc.independents)==numIndependants, "Expecting %(N)s independents but found %(F)s:\r\n%(E)s"%{"F":len(dc.independents), "N":len(numIndependants)}
            dc.independents.sort()
            indis.sort()
            #    Check the independents:
            assert dc.independents==indis, "Different independent uIds: %(A)s to that expected: %(E)s"%{"A":dc.independents, "E":indis}
            #    Check the maxDepth:
            maxDepth = Checker.maxDepth(dc.allHierarchies)
            assert maxDepth==eMaxDepth, "Max depth: %(A)s is different to that expected: %(E)s"%{"A":maxDepth, "E":eMaxDepth}
            #    Now satisfy the dependencies in order as they become available:
            assert len(dc.independents)==1
            assert dc.independents[0]==1
            def dump(txt, dc):
                print txt+"\n"
                print "allHeirarchies:\n%(A)s"%{"A":dc.allHierarchies}
                print "dependencyMap:\n%(A)s"%{"A":dc.dependencyMap}
                try:
                    print "independents:\n%(A)s"%{"A":dc.independents}
                except NoRootException, _e:
                    print "No roots remaining!"
            dump("Start", dc)
            try:
                lah = len(dc.allHierarchies)
                ldm = len(dc.dependencyMap)
                m1 = dc.next()
                #    Recycle the first root:
                dc.recycle(m1)
                assert len(dc.pending)==0
                assert len(dc.satisfied)==0
                assert len(dc.allHierarchies)==lah
                assert len(dc.dependencyMap)==ldm
                #    And get it again:
                m2 = dc.next()
                assert m1==m2
                try:
                    #    There is only one root until it is satisfied, NoRootException will be raised:
                    dc.next()
                except NoRootException, _e:
                    assert True
                    dc.satisfy(m2)
                    #    Now there are >0 roots:
                else:
                    assert False
                while True:
                    #    We can only satisfy independents:
                    m = dc.next()
                    dc.satisfy(m)
                    dump("satisfied: '%(S)s'."%{"S":m}, dc)
            except NoRootException, _e:
                dump("End", dc)
                #    Make sure we're all done:
                assert len(dc.allHierarchies)==0
                assert len(dc.dependencyMap)==0
                assert len(dc.pending)==0
                #    And completely satisfied!
                for i in xrange(1, endId+1):
                    assert i in dc.satisfied
            else:
                dump("Error", dc)
                assert False
    def testNoRoot(self):
        items = []
        numIndependants = 0
        numUnsatisfied = 0
        indis = []
        for _i in range (0, numIndependants):
            indis.append((self.id.next()))        #0 INVALID
        items.extend(indis)
        items.append((self.id.next(), [1,2]))     #1
        items.append((self.id.next(), [1]))     #2
        unsat = []
        unsats = []
        for _i in range(0, numUnsatisfied):
            id_ = self.id.next()
            unsats.append(id_)
            unsat.append((id_, [1000+_i]))
        items.extend(unsat)
        try:
            Checker.verify(items)
        except NoRootException, _e:
            assert True, "Correctly raised exception!"
        else:
            assert False, "No NoNonDependendents found!"
    def testDependencyMapping(self):
        (items, _independents, _allHierarchies, dependencyMap) = self.testHappyPath()
        assert len(dependencyMap)==len(items), "Invalid dependencyMap!"
        tm = {}
        for i in range(0, len(dependencyMap)):
            k = i+1
            tm[k] = "%(N)d"%{"N":k}
        mapping = Checker.applyMapping(dependencyMap, tm)
        assert len(mapping)==len(dependencyMap), "Invalid mapping!"

if __name__=="__main__":
    unittest.main()
