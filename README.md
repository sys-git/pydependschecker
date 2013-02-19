pydependschecker
================

A pure-python dependency graph generator and checker

Checks hierarchical dependency graphs in the form [(int_id, [dependency_int_ids])].

Creates a flattened dependency graph from supplied list of dependencies,
Checks for:
  Circular dependencies,
  Self dependencies,
  Common dependency root (non-dependants),
  Missing (unsatisfied) dependencies.

The resultant graph can then have a mapping
applied (in the form {int_id: objN}) and the resultant graph returned: [obj1:[obj2, obj3], obj1:[obj2, obj5]].

Alternatively you can use the DependencyChecker instance to act as a psudo generator
by using the next(), recycle() and satisfy() methods.



Example taken from one of the unit-tests:
uIds: 1, 2 and 3 have no dependencies,
uId: 4 depends on uIds: 1 and 2
uId: 5 depends on uIds: 1 and 4
uId: 6 depends on uIds: 1, 3 and 4

    dc = Checker.verify([1, 2, 3, (4, [1, 2]), (5, [1, 4]), (6, [1, 3, 4])])
    dc.next()
  > 1
    dc.next()
  > 2
    dc.next()
  > 3
    dc.next()
  > NoRootException
    dc.pending
  > [1, 2, 3]
    dc.recycle(1)
    dc.next()
  > 1
    dc.next()
  > NoRootException
    dc.satisfy(1)
    dc.pending
  > [2, 3]
    dc.next()
  > NoRootException
    dc.satisfy(2)
    dc.next()
  > 4
    dc.satisfy(3)
    dc.next()
  > NoRootException
    dc.satisfy(4)
    dc.satisfy(5)
    dc.satisfy(6)
    dc.next()
  > NoRootException
    dc.pending
  > []
    dc.satisfied
  > [1, 2, 3, 4, 5, 6]
